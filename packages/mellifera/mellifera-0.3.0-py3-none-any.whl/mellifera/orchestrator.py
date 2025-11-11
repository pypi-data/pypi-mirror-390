from __future__ import annotations

from abc import ABC, abstractmethod
from types import SimpleNamespace
import functools
import logging

from typing import TYPE_CHECKING, Any, Optional
import threading

from mellifera.executor import Executor
from mellifera.services import TrioService, NSMainThreadService

if TYPE_CHECKING:
    from mellifera.service import Service

def threadsafe(f):
    @functools.wraps(f)
    def inner(self, *args, **kwargs):
        return self.run_threadsafe(f, self, *args, **kwargs)

    return inner

class Orchestrator:

    def __init__(self, stop_on_finish=True) -> None:
        self.logger = logging.getLogger("calsiprovis.orchestrator.ParentOrchestrator")
        self.services = SimpleNamespace()

        from mellifera.executors import TrioExecutor, HAS_NSMAINTHREAD
        if HAS_NSMAINTHREAD:
            from mellifera.executors import NSMainThreadExecutor


        self.executors: dict[str, Executor] = {"trio": TrioExecutor(self)}

        if HAS_NSMAINTHREAD:
            self.executors["ns"] = NSMainThreadExecutor(self)

        self.lock = threading.RLock()

    def run_async(self, f, *args, **kwargs):
        self.executors["trio"].run_threadsafe(f, *args, **kwargs)

    def start_service(self, service: Service | str) -> None:
        if isinstance(service, str):
            service = self.get_service(service)
        match service:
            case TrioService():
                self.executors["trio"].start_service(service)
            case NSMainThreadService():
                self.executors["ns"].start_service(service)
            case _:
                raise ValueError(f"Cannot start service of type {type(service)}")

    def stop_service(self, service: Service) -> None:
        match service:
            case TrioService():
                self.executors["trio"].stop_service(service)
            case NSMainThreadService():
                self.executors["ns"].stop_service(service)
            case _:
                raise ValueError(f"Cannot start service of type {type(service)}")

    def register_service(self, service: Service, name: str) -> None:
        with self.lock:
            match service:
                case TrioService():
                    self.executors["trio"].register_service(service, name)
                case NSMainThreadService():
                    if "ns" in self.executors:
                        self.executors["ns"].register_service(service, name)
                    else:
                        raise ValueError("Cannot handle NSMainThreadService, as NSMainThreadExecutor is not available")
                case _:
                    raise ValueError(f"Cannot handle service of type {type(service)}")
            setattr(self.services, name, service)

    def enable_service(self, service: Service, name: str) -> None:
        self.register_service(service, name)
        self.start_service(service)

    def get_service(self, name: str) -> Service:
        with self.lock:
            if hasattr(self.services, name):
                return getattr(self.services, name)
            else:
                raise ValueError(f"Service with name `{name}` not found")

    def run(self):
        if "ns" in self.executors:
            self.executors["trio"].start_sync()
            self.executors["ns"].run_sync()
        else:
            self.executors["trio"].run_sync()

    def stop_all(self):
        for executor in self.executors.values():
            executor.stop_all()

