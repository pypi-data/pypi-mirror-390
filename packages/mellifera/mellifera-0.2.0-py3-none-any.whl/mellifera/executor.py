from abc import ABC, abstractmethod

from mellifera.service import Service

class Executor(ABC):

    @abstractmethod
    def run_threadsafe(self, f, *args, **kwargs):
        """Run function f with args and kwargs inside executor in a threadsafe matter

        This function is threadsafe.
        """
        ...

    @abstractmethod
    def register_service(self, service: Service, name: str) -> None:
        """Register `service` under `name`

        Only makes the service known, does not automatically start it
        """
        ...

    @abstractmethod
    def start_service(self, service: Service) -> None:
        """Start `service` eventually

        Idempotent
        """
        ...

    @abstractmethod
    def stop_service(self, service: Service) -> None:
        """Stop `service` eventually

        Idempotent
        """
        ...

    @abstractmethod
    def stop_all(self) -> None:
        """Stops all services

        Idempotent
        """
        ...

    @abstractmethod
    def start_sync(self) -> None:
        """Start the executor.

        Returns after the executor is started (in a different thread or process)
        """
        ...

    @abstractmethod
    def run_sync(self) -> None:
        """Run the executor

        Returns after the executor is done
        """
        ...
