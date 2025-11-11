try:
    from Foundation import NSThread
    from libdispatch import dispatch_async, dispatch_sync, dispatch_get_main_queue
except ModuleNotFoundError:
    raise ModuleNotFoundError("To use mellifera.orchestrators.nsmainthread you need to have pyobjc installed and run on macos")

from types import SimpleNamespace
import logging

from mellifera.orchestrator import Orchestrator, threadsafe
from mellifera.services.nsmainthread import NSMainThreadService
from mellifera.service import Service
from mellifera.executor import Executor

from mellifera.service import ServiceState

class NSMainThreadExecutor(Executor):
    requires_run = True

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        self.service = None
        self.logger = logging.getLogger("mellifera.executors.NSMainThreadExecutor")

    def run_threadsafe(self, f, *args, **kwargs):
        self.logger.info(f"Running {f} with args {args} {kwargs}")
        if self.service and self.service.state == ServiceState.RUNNING:
            def closure():
                return f(*args, **kwargs)

            self.logger.info("Getting queue")
            queue = dispatch_get_main_queue()
            self.logger.info(f"Queue is {queue}")

            self.logger.info("dispatching")
            r = dispatch_async(queue, closure)
            self.logger.info("dispatch done")

            return r
        else:
            return f(*args, **kwargs)

    @threadsafe
    def register_service(self, service: Service, name: str) -> None:
        assert isinstance(service, NSMainThreadService)
        service.register(self.orchestrator, self, name)

    @threadsafe
    def start_service(self, service: Service) -> None:
        if self.service is not None and self.service != service:
            raise ValueError(f"Can only start a single service, already starting {self.service}")
        if self.service is None:
            self.service = service
            service.state = ServiceState.WILL_BE_STARTED

    @threadsafe
    def stop_service(self, service: Service) -> None:
        assert isinstance(service, NSMainThreadService)
        service.stop()

    @threadsafe
    def stop_all(self) -> None:
        self.service.stop()

    def start_sync(self) -> None:
        raise NotImplementedError()

    def run_sync(self) -> None:
        self.logger.debug("Starting up")
        if self.service:
            try:
                self.logger.debug("Initializing service")
                self.service.init_sync()
                self.logger.debug("Running service")
                self.service.run_sync()
                self.logger.debug("Running service done, stopping")
                self.orchestrator.stop_all()
            finally:
                self.service.finalize_sync()
