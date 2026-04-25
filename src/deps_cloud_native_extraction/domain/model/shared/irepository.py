from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

__all__ = ["IExtractorRepository"]

TExtractor = TypeVar("TExtractor")
TInfo = TypeVar("TInfo")


class IExtractorRepository(ABC, Generic[TExtractor, TInfo]):
    @abstractmethod
    def get(self, id_: str, tenant_id: str) -> Optional[TExtractor]:
        ...

    @abstractmethod
    def save(self, extractor: TExtractor) -> None:
        ...

    @abstractmethod
    def delete(self, id_: str, tenant_id: str) -> None:
        ...

    @abstractmethod
    def get_extractor_info(self, id_: str, tenant_id: str) -> Optional[TInfo]:
        ...
