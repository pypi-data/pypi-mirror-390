import trio
from typing import final

from mellifera.service import Service, ServiceState, ServiceError


class TrioService(Service):

    def __init__(self):
        super().__init__()

        self._nursery = None
        self._trio_token = None
        self._stopped = trio.Event()
        self._default_is_running = trio.Event()
        self._dependents = []
        self._dependencies = []
        self._requires = []
        self.cancel_scope = trio.CancelScope()

    @final
    async def init(self) -> None:
        if self.state != ServiceState.WILL_BE_STARTED:
            raise ServiceError(
                f"Trying to initate a service that is in state {self.state.name}"
            )
        assert self.name
        assert self.orchestrator
        assert self.executor
        self.state = ServiceState.INITIATING

        for dependency in self._dependencies:
            self.orchestrator.start_service(dependency)
        for dependency in self._dependencies:
            await dependency.initiated
        for dependency in self._requires:
            await dependency.initiated
        await self._init()
        self.state = ServiceState.INITIATED

    @final
    async def run(self) -> None:
        if self.state != ServiceState.INITIATED:
            raise ServiceError(
                f"Trying to initate a service that is in state {self.state.name}"
            )
        self.state = ServiceState.RUNNING

        try:
            with self.cancel_scope:
                await self._run()
            await self.stop()
        finally:
            self.state = ServiceState.STOPPED
            self._nursery = None

    @final
    async def stop(self) -> None:
        if self.state.value >= ServiceState.STOPPING.value:
            return
        if self.state == ServiceState.RUNNING:
            self.state = ServiceState.STOPPING
            for dependent in self._dependents:
                self.logger.debug(f"Waiting for {dependent.name}")
                await dependent.stopped
                self.logger.debug(f"Waiting for {dependent.name} DONE")
            await self._stop()
        else:
            self.state = ServiceState.STOPPING
            self.state = ServiceState.STOPPED

    def requires(self, name: str) -> Service:
        if not self.orchestrator:
            raise ValueError("Service is not attached to an orchestrator")
        service = self.orchestrator.get_service(name)
        self._requires.append(service)
        return service

    def depends_on(self, name: str) -> Service:
        if not self.orchestrator:
            raise ValueError("Service is not attached to an orchestrator")
        service = self.orchestrator.get_service(name)
        assert isinstance(service, TrioService)
        self._dependencies.append(service)
        service._dependents.append(self)
        return service

    def uses(self, name: str) -> Service:
        if not self.orchestrator:
            raise ValueError("Service is not attached to an orchestrator")
        service = self.orchestrator.get_service(name)
        return service



    async def start(self, nursery: trio.Nursery, task_status=trio.TASK_STATUS_IGNORED) -> None:
        task_status.started()
        return


    @final
    async def cancel(self) -> None:
        self.logger.debug("Cancelling")
        if self._nursery:
            self._nursery.cancel_scope.cancel()
        self.logger.debug("Cancelling Done")

    @final
    async def finalize(self) -> None:
        if self.state.value < ServiceState.STOPPED.value:
            self.logger.error(
                f"shut_down called for service {self.name}, but in state {self.state.name}"
            )
        if self.state == ServiceState.SHUTDOWN:
            self.logger.error(
                f"shut_down called for service {self.name}, but in state {self.state.name}"
            )
            return

        self.state = ServiceState.SHUTDOWN_STARTED
        await self._finalize()
        self.state = ServiceState.SHUTDOWN

    def _construct(self) -> None:
        """Override to request other services
        """
        pass

    async def _init(self) -> None:
        """Override to customize initialization.

        Aquire ressources here
        """
        pass

    async def _run(self) -> None:
        """Override to customize running behavior"""
        await trio.sleep_forever()

    async def _stop(self) -> None:
        """Override to stop running"""
        self.cancel_scope.cancel()

    async def _finalize(self) -> None:
        """Override to close all ressources aquired on _init"""
        pass
