from typing import Optional

from deps_cloud_native_extraction.domain.model import (
    AzureDIExtractor,
    AzureExtractorInfo,
    IExtractorRepository,
)

__all__ = ["FakeAzureExtractorRepository"]


class FakeAzureExtractorRepository(IExtractorRepository):
    def __init__(self) -> None:
        self._db: dict[tuple[str, str], AzureDIExtractor] = {}

    def save(self, extractor: AzureDIExtractor) -> None:
        self._db[(extractor.id(), extractor.tenant_id())] = extractor

    def get(self, id_: str, tenant_id: str) -> Optional[AzureDIExtractor]:
        return self._db.get((id_, tenant_id))

    def delete(self, id_: str, tenant_id: str) -> None:
        self._db.pop((id_, tenant_id), None)

    def get_extractor_info(self, id_: str, tenant_id: str) -> Optional[AzureExtractorInfo]:
        if extractor := self._db.get((id_, tenant_id)):
            return AzureExtractorInfo(
                id=extractor.id(),
                model_id=extractor.model_id,
                endpoint=extractor.endpoint,
            )
