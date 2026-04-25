from typing import Protocol

from deps_extracted_data import ExtractedData

__all__ = ["IExtractDocuments"]


class IExtractDocuments(Protocol):
    def perform_extraction(
        self,
        document_id: str,
        tenant_id: str,
        extractor_id: str,
    ) -> ExtractedData:
        pass
