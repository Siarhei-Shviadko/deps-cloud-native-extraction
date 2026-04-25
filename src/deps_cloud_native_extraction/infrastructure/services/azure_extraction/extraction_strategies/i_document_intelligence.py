from typing import Protocol

from azure.ai.documentintelligence import (
    DocumentIntelligenceAdministrationClient,
    DocumentIntelligenceClient,
)
from deps_extracted_data import ExtractedData

from deps_cloud_native_extraction.domain.model import AzureDIField, FieldCode

__all__ = ["IDocumentIntelligenceExtractor"]


class IDocumentIntelligenceExtractor(Protocol):
    def extract(
        self,
        document_id: str,
        model_id: str,
        data: ExtractedData,
        extractor_schema: dict[FieldCode, AzureDIField],
        extraction_client: DocumentIntelligenceClient,
        admin_client: DocumentIntelligenceAdministrationClient,
    ) -> ExtractedData:
        ...
