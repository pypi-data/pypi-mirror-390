from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mellifera.orchestrator import Orchestrator
    from logging import Logger
    from mellifera.executor import Executor

import trio
from typing import final
import logging
from functools import wraps
from enum import Enum



class ServiceError(Exception):
    pass


class ServiceState(Enum):
    NONE = 0
    CONSTRUCTED = 1
    WILL_BE_STARTED = 2
    INITIATING = 3
    INITIATED = 4
    RUNNING = 5
    STOPPING = 6
    STOPPED = 7
    SHUTDOWN_STARTED = 8
    SHUTDOWN = 9


def expose(f):
    @wraps(f)
    def _inner(service, *args, **kwargs):
        if (not service.state == ServiceState.INITIATED) and (
            not service.state == ServiceState.RUNNING
        ):
            raise RuntimeError(
                f"Service `{service.name}` not running, but is in state {service.state}"
            )
        return service.orchestrator.run_threadsafe(f, service, *args, **kwargs)

    return _inner


class Service:

    orchestrator: Orchestrator
    executor: Executor
    logger: Logger
    name: str

    def __init__(self) -> None:
        self._state = ServiceState.NONE

        self.initiated_event = trio.Event()
        self.started_event = trio.Event()
        self.stopped_event = trio.Event()
        self.shutdown_event = trio.Event()


    @property
    def initiated(self):
        return self.initiated_event.wait()

    @property
    def started(self):
        return self.started_event.wait()

    @property
    def stopped(self):
        return self.stopped_event.wait()

    @property
    def shutdown(self):
        return self.shutdown_event.wait()

    @property
    def state(self) -> ServiceState:
        return self._state

    @state.setter
    def state(self, state: ServiceState) -> None:
        match state:
            case ServiceState.NONE:
                assert False
            case ServiceState.CONSTRUCTED:
                if self._state != ServiceState.NONE:
                    raise ServiceError(
                        f"Trying to set service {self.name} into state {state.name} which is in state {self.state.name}"
                    )
                self._state = state
            case ServiceState.WILL_BE_STARTED:
                if self._state != ServiceState.CONSTRUCTED:
                    raise ServiceError(
                        f"Trying to set service {self.name} into state {state.name} which is in state {self.state.name}"
                    )
                self._state = state
            case ServiceState.INITIATING:
                if self._state != ServiceState.WILL_BE_STARTED:
                    raise ServiceError(
                        f"Trying to set service {self.name} into state {state.name} which is in state {self.state.name}"
                    )
                self._state = state
                self.logger.debug("Initiating")
            case ServiceState.INITIATED:
                if self._state != ServiceState.INITIATING:
                    raise ServiceError(
                        f"Trying to set service {self.name} into state {state.name} which is in state {self.state.name}"
                    )
                self._state = state
                self.logger.debug("Initiating done")
                self.initiated_event.set()
            case ServiceState.RUNNING:
                if self._state != ServiceState.INITIATED:
                    raise ServiceError(
                        f"Trying to set service {self.name} into state {state.name} which is in state {self.state.name}"
                    )
                self._state = state
                self.logger.debug("Running")
                self.started_event.set()
            case ServiceState.STOPPING:
                if self._state.value >= state.value:
                    raise ServiceError(
                        f"Trying to set service {self.name} into state {state.name} which is in state {self.state.name}"
                    )
                self._state = state
                self.logger.debug("Stopping")
            case ServiceState.STOPPED:
                if (self._state != ServiceState.RUNNING) and (
                    self._state != ServiceState.STOPPING
                ):
                    raise ServiceError(
                        f"Trying to set service {self.name} into state {state.name} which is in state {self.state.name}"
                    )
                self._state = state
                self.logger.debug("Stopped")
                self.stopped_event.set()
            case ServiceState.SHUTDOWN_STARTED:
                self._state = state
                self.logger.debug("Shutting Down")
            case ServiceState.SHUTDOWN:
                if self._state != ServiceState.SHUTDOWN_STARTED:
                    raise ServiceError(
                        f"Trying to set service {self.name} into state {state.name} which is in state {self.state.name}"
                    )
                self._state = state
                self.logger.debug("Shutting Down Done")
                self.shutdown_event.set()

    def register(self, orchestrator, executor, name):
        self.orchestrator = orchestrator
        self.executor = executor
        self.name = name
        self._register()
        self.state = ServiceState.CONSTRUCTED
        self.logger = logging.getLogger(f"mellifera.service.{name}")

    def _register(self):
        pass

    @final
    def init_sync(self) -> None:
        if self.state != ServiceState.CONSTRUCTED:
            raise ServiceError(
                f"Trying to initate a service that is in state {self.state.name}"
            )
        self.state = ServiceState.INITIATING
        self._init_sync()
        self.state = ServiceState.INITIATED

    def _init_sync(self) -> None:
        pass

    @final
    def shut_down_sync(self) -> None:
        if self.state.value < ServiceState.STOPPED.value:
            self.logger.error(
                f"shut_down called for service {self.name}, but in state {self.state.name}"
            )
        if self.state.value == ServiceState.SHUTDOWN:
            self.logger.error(
                f"shut_down called for service {self.name}, but in state {self.state.name}"
            )
            return

        self.state = ServiceState.SHUTDOWN_STARTED
        self._shut_down_sync()
        self.state = ServiceState.SHUTDOWN

    def _shut_down_sync(self) -> None:
        pass
