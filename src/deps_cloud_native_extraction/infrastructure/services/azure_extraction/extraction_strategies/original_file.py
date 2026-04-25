import io
import logging

from azure.ai.documentintelligence import (
    AnalyzeDocumentLROPoller,
    DocumentIntelligenceAdministrationClient,
    DocumentIntelligenceClient,
)
from azure.ai.documentintelligence.models import AnalyzeResult, DocumentModelDetails
from deps_extracted_data import ExtractedData

from deps_cloud_native_extraction.domain.model import AzureDIField, FieldCode
from deps_cloud_native_extraction.infrastructure.proxies import (
    DocumentProxy,
    UnifierProxy,
)

from ..converters import AzureResponseConverter
from .i_document_intelligence import IDocumentIntelligenceExtractor

__all__ = ["OriginalFileDIExtraction"]


class OriginalFileDIExtraction(IDocumentIntelligenceExtractor):
    def __init__(
        self,
        unifier_proxy: UnifierProxy,
        document_proxy: DocumentProxy,
    ) -> None:
        self._unifier = unifier_proxy
        self._documents = document_proxy

        self._logger = logging.getLogger(self.__class__.__name__)

    def extract(
        self,
        document_id: str,
        model_id: str,
        data: ExtractedData,
        extractor_schema: dict[FieldCode, AzureDIField],
        extraction_client: DocumentIntelligenceClient,
        admin_client: DocumentIntelligenceAdministrationClient,
    ) -> ExtractedData:
        self._logger.info(
            "Extraction for document %s with model %s has been started...",
            document_id,
            model_id,
        )

        blob: bytes = self._documents.get_original_file(document_id=document_id)

        with io.BytesIO(blob) as stream:
            poller: AnalyzeDocumentLROPoller[AnalyzeResult] = extraction_client.begin_analyze_document(
                model_id=model_id,
                body=stream,
            )

        result: AnalyzeResult = poller.result()
        model_details: DocumentModelDetails = admin_client.get_model(model_id)

        # Azure prebuilt models have a docType without the `prebuilt-` suffix
        document_type_id = model_id.removeprefix("prebuilt-")

        AzureResponseConverter.handling_response(
            azure_extractor_type_response=model_details.doc_types[document_type_id],
            extractor_schema=extractor_schema,
            azure_extraction_response=result,
            unified_images=self._unifier.get_original_images(document_id=document_id),
        ).compose_extracted_data(edata=data)

        return data
