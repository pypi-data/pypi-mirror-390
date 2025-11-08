import threading
import logging
from types import SimpleNamespace

from mellifera.orchestrator import Orchestrator
from mellifera.service import Service


class ParentOrchestrator(Orchestrator):

    def __init__(self, stop_on_finish=True) -> None:
        self.logger = logging.getLogger("calsiprovis.orchestrator.ParentOrchestrator")
        self.children = []
        self._called_stop = False
        self.running = False
        self._service_namespace = None
        self._lock = threading.RLock()
        self.stop_on_finish = stop_on_finish

    def add_orchestrator(self, orchestrator: Orchestrator) -> None:
        with self._lock:
            self.children.append(orchestrator)
            orchestrator.parent = self

    def can_handle(self, service: Service) -> bool:
        with self._lock:
            for orchestrator in self.children:
                if orchestrator.can_handle(service):
                    return True
            return False

    @property
    def services(self) -> SimpleNamespace:
        if not self._service_namespace:
            with self._lock:
                services = SimpleNamespace()
                for orchestrator in self.children:
                    for name, service in orchestrator._services.items():
                        setattr(services, name, service)
                self._service_namespace = services
        return self._service_namespace

    def register_service(self, service: Service, name: str) -> None:
        with self._lock:
            for orchestrator in self.children:
                if orchestrator.can_handle(service):
                    orchestrator._register_service(service, name)
                    break
            else:
                raise ValueError(f"Service of unknown type {type(service)}")
            self._service_namespace = None

    def get_service(self, name: str) -> Service:
        with self._lock:
            for orchestrator in self.children:
                try:
                    service = orchestrator._get_service(name)
                    return service
                except ValueError:
                    pass
            raise ValueError(f"Service with name `{name}` not found")

    def construct(self) -> None:
        with self._lock:
            for orchestrator in self.children:
                orchestrator.construct()

    def start_sync(self) -> None:
        raise NotImplementedError()

    def run_sync(self) -> None:
        self.running = True
        start = []
        run = []
        with self._lock:
            for orchestrator in self.children:
                if orchestrator.requires_run:
                    run.append(orchestrator)
                else:
                    start.append(orchestrator)

        try:
            with self._lock:
                for orchestrator in self.children:
                    orchestrator.construct()

            if len(run) > 1:
                raise ValueError(
                    f"Need to run {len(run)} many Orchestrators, can only run 1."
                )

            for orchestrator in run:
                orchestrator.init_sync()

            for orchestrator in start:
                orchestrator.start_sync()

            for orchestrator in run:
                orchestrator.run_sync()
        finally:
            if self.stop_on_finish:
                self.stop_sync()
            self.running = False

    def stop_sync(self) -> None:
        if not self._called_stop:
            self._called_stop = True
            with self._lock:
                for orchestrator in self.children:
                    orchestrator.stop_sync(bubble=False)
