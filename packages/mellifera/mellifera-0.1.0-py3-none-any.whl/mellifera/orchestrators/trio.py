from typing import TYPE_CHECKING

import trio
import trio.lowlevel
import threading
import inspect
import logging
from queue import Queue
from types import SimpleNamespace

from mellifera.services.trio import TrioService, ServiceState
from mellifera.orchestrator import Orchestrator, run_threadsafe as _run_threadsafe
from mellifera.service import Service


class TrioOrchestrator(Orchestrator):
    requires_run = False

    def __init__(self) -> None:
        self._services = {}
        self.trio_token = None
        self._called_construct = False
        self._called_init = False
        self._called_run = False
        self._called_stop = False
        self._called_shut_down = False
        self.parent = None
        self._service_namespace = None
        self.logger = logging.getLogger("calsiprovis.orchestrator.TrioOrchestrator")
        self._thread = None
        self._lock = threading.RLock()

    def run_threadsafe(self, f, *args, **kwargs):
        if trio.lowlevel.in_trio_run():
            return f(*args, **kwargs)
        else:
            # Orchestrator didn't start yet, use locking for synchronisation
            if not self._thread:
                with self._lock:
                    return f(*args, **kwargs)
            else:
                if self.trio_token:
                    if inspect.iscoroutinefunction(f):

                        async def closure():
                            return await f(*args, **kwargs)

                        return trio.from_thread.run(closure, trio_token=self.trio_token)
                    else:

                        def closure():
                            return f(*args, **kwargs)

                        return trio.from_thread.run_sync(
                            closure, trio_token=self.trio_token
                        )
                else:
                    raise ValueError(
                        "Calling TrioOrchestrator.run_in_thread but trio_token is None"
                    )

    def can_handle(self, service: Service) -> bool:
        return isinstance(service, TrioService)

    @property
    def services(self) -> SimpleNamespace:
        if not self._service_namespace:
            services = SimpleNamespace()
            for name, service in self._services.items():
                setattr(services, name, service)
            self._service_namespace = services
        return self._service_namespace

    def register_service(self, service: Service, name: str) -> None:
        if self.parent:
            return self.parent.register_service(service, name)
        return self._register_service(service, name)

    @_run_threadsafe
    def _register_service(self, service: Service, name: str) -> None:
        assert isinstance(service, TrioService)
        service.orchestrator = self
        service.name = name
        self._services[name] = service
        self._service_namespace = None

    def get_service(self, name: str) -> Service:
        if self.parent:
            return self.parent.get_service(name)
        return self._get_service(name)

    @_run_threadsafe
    def _get_service(self, name: str) -> Service:
        service = self._services.get(name)
        if not service:
            raise ValueError(f"Service with name `{name}` not found")
        return service

    def construct(self) -> None:
        if not self._called_construct:
            self._called_construct = True
            for service in self._services.values():
                service.construct()

    async def init(self) -> None:
        if not self._called_init:
            self.logger.info("Initiating")
            self._called_init = True
            self.construct()
            async with trio.open_nursery() as nursery:
                for service in self._services.values():
                    nursery.start_soon(service.init)
            self.logger.info("Initiating Done")

    async def run(self, queue: Queue) -> None:
        self.construct()
        self._called_run = True

        try:
            await self.init()
        except Exception as e:
            self.logger.error("Error occured during initialisation")
            queue.put(e)
            raise e

        trio_token = trio.lowlevel.current_trio_token()
        queue.put(trio_token)

        try:
            await self._run()
            await self.stop()
        except Exception as e:
            self.logger.error("Error occured during _run or stop")
            raise e
        finally:
            try:
                self.logger.debug("Stopping")
                await self.stop()
                self.logger.debug("Stopping done")
            finally:
                self.logger.debug("shutting down")
                await self.shut_down()
                self.logger.debug("shutting down done")

    async def _run(self) -> None:
        self.logger.debug("Running")
        async with trio.open_nursery() as nursery:
            for service in self._services.values():
                nursery.start_soon(service.run)
        self.logger.debug("Running Done")

    async def stop(self, bubble=True) -> None:
        if not self._called_stop:
            self._called_stop = True
            if bubble and self.parent:
                self.parent.stop_sync()
            await self._stop()

    async def _stop(self) -> None:
        self.logger.error("Stopping")
        try:
            with trio.move_on_after(5):
                async with trio.open_nursery() as nursery:
                    for name, service in self._services.items():
                        nursery.start_soon(service.stop)
        finally:
            with trio.move_on_after(10):
                async with trio.open_nursery() as nursery:
                    for service in self._services.values():
                        if service.state.value < ServiceState.STOPPED.value:
                            self.logger.warn(
                                f"Service {service.name} is in state {service.state.name} , cancelling"
                            )
                            nursery.start_soon(service.cancel)
        self.logger.error("Stopped")

    async def shut_down(self) -> None:
        if not self._called_shut_down:
            self.logger.error("Shutting Down")
            self._called_shut_down = True
            with trio.CancelScope(shield=True):
                async with trio.open_nursery() as nursery:
                    for service in self._services.values():
                        nursery.start_soon(service.shut_down)
            self.logger.error("Shut Down")

    def start_sync(self) -> None:
        try:
            self.logger.debug("Starting Sync")
            queue = Queue()
            self._thread = threading.Thread(target=trio.run, args=(self.run, queue))
            self._thread.start()
            self.logger.debug("Waiting for value")
            value = queue.get()
            self.logger.debug("Got value")
            if isinstance(value, Exception):
                raise value
            else:
                self.trio_token = value
            self.logger.debug("Starting Sync Done")
        except BaseException as e:
            # self.logger.error("Exception occured during start_sync", exc_info=True)
            # for name, service in self._services.items():
            # self.logger.error(f"Service {name} is in state {service.state}")
            raise e

    def run_sync(self) -> None:
        raise NotImplementedError()

    def stop_sync(self, bubble=True) -> None:
        return self.run_threadsafe(self.stop, bubble=bubble)
