try:
    from Foundation import NSThread
    from libdispatch import dispatch_async, dispatch_sync, dispatch_get_main_queue
except ModuleNotFoundError:
    raise ModuleNotFoundError("To use mellifera.orchestrators.nsmainthread you need to have pyobjc installed and run on macos")

from types import SimpleNamespace

from mellifera.orchestrator import Orchestrator
from mellifera.services.nsmainthread import NSMainThreadService
from mellifera.service import Service


class NSMainThreadOrchestrator(Orchestrator):
    requires_run = True

    def __init__(self) -> None:
        self._services = {}
        self._called_construct = False
        self._called_init = False
        self._called_run = False
        self._called_stop = False
        self._called_shut_down = False
        self.parent = None
        self._service_namespace = None

    def run_threadsafe(self, f, *args, **kwargs):
        if NSThread.isMainThread():
            return f(*args, **kwargs)
        else:

            def closure():
                return f(*args, **kwargs)

            return dispatch_sync(dispatch_get_main_queue(), closure)

    @property
    def services(self) -> SimpleNamespace:
        if not self._service_namespace:
            services = SimpleNamespace()
            for name, service in self._services.items():
                setattr(services, name, service)
            self._service_namespace = services
        return self._service_namespace

    def can_handle(self, service: Service) -> bool:
        return isinstance(service, NSMainThreadService)

    def register_service(self, service: Service, name: str) -> None:
        if self.parent:
            return self.parent.register_service(service, name)
        assert isinstance(service, NSMainThreadService)
        return self._register_service(service, name)

    def _register_service(self, service: NSMainThreadService, name: str) -> None:
        assert isinstance(service, NSMainThreadService)
        service.orchestrator = self
        service.name = name
        self._services[name] = service
        self._service_namespace = None
        if len(self._services) > 1:
            raise ValueError(
                "MainThreadOrchestrator has multiple services to manage, can only orchestrate a single MainThreadService"
            )

    def get_service(self, name: str) -> Service:
        if self.parent:
            return self.parent.get_service(name)
        return self._get_service(name)

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

    def init_sync(self) -> None:
        if not self._called_init:
            self._called_init = True
            for service in self._services.values():
                service.init_sync()

    def start_sync(self) -> None:
        raise NotImplementedError()

    def run_sync(self) -> None:
        self.construct()
        self.init_sync()

        try:
            self._run_sync()
            self.stop_sync()
        finally:
            try:
                self.stop_sync()
            finally:
                self.shut_down_sync()

    def _run_sync(self) -> None:
        for service in self._services.values():
            service.run_sync()

    def stop_sync(self, bubble: bool=True) -> None:
        if not self._called_stop:
            self._called_stop = True
            if bubble and self.parent:
                self.parent.stop_sync()
            self._stop_sync()

    def _stop_sync(self) -> None:
        for service in self._services.values():
            service.stop_sync()

    def shut_down_sync(self) -> None:
        for service in self._services.values():
            service.shut_down_sync()
