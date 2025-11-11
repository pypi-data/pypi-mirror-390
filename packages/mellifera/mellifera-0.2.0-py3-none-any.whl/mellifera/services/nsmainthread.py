from mellifera.service import Service, ServiceState, ServiceError
from typing import final


class NSMainThreadService(Service):

    def stop_sync(self) -> None:
        if self.state.value >= ServiceState.STOPPING.value:
            return
        if self.state == ServiceState.RUNNING:
            self.state = ServiceState.STOPPING
            self._stop_sync()
        else:
            self.state = ServiceState.STOPPING
            self.state = ServiceState.STOPPED

    def run_sync(self) -> None:
        if self.state != ServiceState.INITIATED:
            raise ServiceError(
                f"Trying to initate a service that is in state {self.state.name}"
            )
        self.state = ServiceState.RUNNING

        try:
            self._run_sync()
            self.stop_sync()
        finally:
            self.state = ServiceState.STOPPED
            self._nursery = None

    def _run_sync(self) -> None:
        pass

    @final
    def stop(self) -> None:
        if self.state.value >= ServiceState.STOPPING.value:
            return
        self.state = ServiceState.STOPPING
        self._stop_sync()

    def _stop_sync(self) -> None:
        pass

    @final
    def shut_down_sync(self) -> None:
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
        self._shut_down_sync()
        self.state = ServiceState.SHUTDOWN

    def _shut_down_sync(self) -> None:
        pass
