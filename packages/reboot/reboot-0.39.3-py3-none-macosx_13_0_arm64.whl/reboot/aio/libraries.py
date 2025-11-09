from __future__ import annotations

from abc import ABC, abstractmethod
from rebootdev.aio.external import InitializeContext
from rebootdev.aio.servicers import Servicer
from typing import ClassVar


class AbstractLibrary(ABC):
    """
    Defines methods a Library needs that do NOT require `Application`.

    See `Library` reboot.aio.applications for other defined methods.
    """
    name: ClassVar[str]

    @abstractmethod
    def servicers(self) -> list[type[Servicer]]:
        raise NotImplementedError

    def dependencies(self) -> list[str]:
        return []

    async def initialize(self, context: InitializeContext) -> None:
        """
        A function to allow libraries to run initialize steps after the
        `Application` has started.
        """
        pass
