from typing import TYPE_CHECKING

import trio
import trio.lowlevel
import threading
import inspect
import logging
from queue import Queue
from types import SimpleNamespace

from mellifera.services.trio import TrioService, ServiceState
from mellifera.orchestrator import Orchestrator, threadsafe
from mellifera.service import Service
from mellifera.executor import Executor


class TrioExecutor(Executor):
    requires_run = False

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        self.trio_token = None
        self.services = []
        self.logger = logging.getLogger("mellifera.executors.TrioExecutor")

        self.nursery = None
        self.to_start = []
        self._thread = None
        self._lock = threading.RLock()
        self.stopped = trio.Event()

        self.write_channel, self.read_channel = trio.open_memory_channel(100)

    def run_threadsafe(self, f, *args, **kwargs):
        self.logger.info(f"run_threadsafe {f.__name__}")

        if inspect.iscoroutinefunction(f):
            async def closure():
                return await f(*args, **kwargs)
            is_async = True
        else:
            def closure():
                return f(*args, **kwargs)
            is_async = False

        if trio.lowlevel.in_trio_run():
            if is_async:
                try:
                    return self.write_channel.send_nowait(closure)
                except trio.BrokenResourceError as e:
                    self.logger.info("broken ressource error")
                    raise e

            else:
                return closure()
        else:
            # Orchestrator didn't start yet, use locking for synchronisation
            if not self._thread:
                with self._lock:
                    if is_async:
                        self.logger.info(f"run_threadsafe {f.__name__} with lock, trio.run")
                        return trio.run(closure)
                    else:
                        self.logger.info(f"run_threadsafe {f.__name__} with lock, direct")
                        return closure()
            else:
                if self.trio_token:
                    if is_async:
                        self.logger.info(f"run_threadsafe {f.__name__} with trio_token, from_thread.run")
                        return trio.from_thread.run(closure, trio_token=self.trio_token)
                    else:
                        self.logger.info(f"run_threadsafe {f.__name__} with trio_token, from_thread.run_sync")
                        return trio.from_thread.run_sync(
                            closure, trio_token=self.trio_token
                        )
                else:
                    raise ValueError(
                        "Calling TrioOrchestrator.run_in_thread but trio_token is None"
                    )

    @threadsafe
    def register_service(self, service: Service, name: str) -> None:
        assert isinstance(service, TrioService)
        service.register(self.orchestrator, self, name)
        self.services.append(service)

    @threadsafe
    async def start_service(self, service):
        if self.stopped.is_set():
            raise ValueError("Trying to start a service when executor is already stopped")
        if service.state == ServiceState.CONSTRUCTED or service.state == ServiceState.WILL_BE_STARTED:
            if service.state == ServiceState.CONSTRUCTED:
                service.state = ServiceState.WILL_BE_STARTED
            self.services.append(service)
            if self.nursery:
                self.logger.info(f"starting running service {service.name}")
                self.nursery.start_soon(self.run_service, service)
            else:
                self.to_start.append(service)
        else:
            raise ValueError(f"Service is in state {service.state}")

    @threadsafe
    async def stop_service(self, service):
        try:
            with trio.fail_after(5):
                await service.stop()
        except trio.TooSlowError:
            with trio.move_on_after(10):
                await service.cancel()

    @threadsafe
    async def stop_all(self):
        for service in self.services:
            self.stop_service(service)
        await self.write_channel.aclose()

    async def run_service(self, service):
        self.logger.info(f"Running service {service.name}")
        try:
            self.logger.info(f"Initializing service {service.name}")
            await service.init()
            self.logger.info(f"Initialized service {service.name}")
            self.logger.info(f"Running service {service.name}")
            await service.run()
            self.logger.info(f"Running service {service.name} Done")
        finally:
            self.logger.info(f"Finalizing service {service.name}")
            await service.finalize()
            self.logger.info(f"Finalizing service {service.name} Done")

    async def start(self, queue: Queue) -> None:
        trio_token = trio.lowlevel.current_trio_token()
        queue.put(trio_token)
        await self.run()

    async def run(self) -> None:
        async with trio.open_nursery() as nursery:
            self.nursery = nursery
            for service in self.to_start:
                nursery.start_soon(self.run_service, service)
            self.to_start = []

            try:
                async with self.read_channel:
                    async for async_function in self.read_channel:
                        await async_function()
            except trio.ClosedResourceError:
                pass

    def start_sync(self) -> None:
        try:
            queue = Queue()
            self._thread = threading.Thread(target=trio.run, args=(self.start, queue))
            self._thread.start()
            value = queue.get()
            if isinstance(value, Exception):
                raise value
            else:
                self.trio_token = value
        except BaseException as e:
            # self.logger.error("Exception occured during start_sync", exc_info=True)
            # for name, service in self._services.items():
            # self.logger.error(f"Service {name} is in state {service.state}")
            raise e

    def run_sync(self) -> None:
        trio.run(self.run)
