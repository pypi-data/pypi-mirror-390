from __future__ import annotations

from abc import ABC, abstractmethod
from types import SimpleNamespace
import functools

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from mellifera.service import Service


def run_threadsafe(f):
    @functools.wraps(f)
    def inner(self, *args, **kwargs):
        return self.run_threadsafe(f, self, *args, **kwargs)

    return inner


class Orchestrator(ABC):

    parent: Optional["Orchestrator"]

    @property
    @abstractmethod
    def services(self) -> SimpleNamespace: ...

    @abstractmethod
    def can_handle(self, service: Service) -> bool: ...

    @abstractmethod
    def register_service(self, service: Service, name: str) -> None: ...

    @abstractmethod
    def get_service(self, name: str) -> Service: ...

    @abstractmethod
    def construct(self) -> None: ...

    @abstractmethod
    def start_sync(self) -> None: ...

    @abstractmethod
    def run_sync(self) -> None: ...

    @abstractmethod
    def stop_sync(self, bubble: bool = True) -> None: ...
