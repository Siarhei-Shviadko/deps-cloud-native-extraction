import logging

from deps_cloud_native_extraction.infrastructure.proxies import (
    DocumentTypeProxy,
    DocumentTypeProxyError,
    ExtractionProxy,
    ExtractionProxyError,
)
from deps_cloud_native_extraction.infrastructure.services import AzureExtractionService

from .create_azure_extractor_data import CreateAzureExtractorSagaData

__all__ = ["CreateAzureExtractorSteps"]


class CreateAzureExtractorSteps:
    extractor_type = "azure_cloud_extractor"
    extractor_engine = "AZURE_FORM_RECOGNIZER"

    def __init__(
        self,
        extraction_proxy: ExtractionProxy,
        document_type_proxy: DocumentTypeProxy,
        azure_service: AzureExtractionService,
    ) -> None:
        self._extraction_proxy = extraction_proxy
        self._document_type_proxy = document_type_proxy
        self._azure_service = azure_service

        self._logger = logging.getLogger(self.__class__.__name__)

    def create_extractor(self, data: CreateAzureExtractorSagaData) -> None:
        self._logger.debug("Starting <create_extractor> step with data: %s", data.__dict__)
        try:
            doc_type_id = self._extraction_proxy.attach_extractor(
                data.name,
                self.extractor_type,
                engine=self.extractor_engine,
                language=data.language,
                description=data.description,
            )
            data.document_type_id = doc_type_id

        except ExtractionProxyError as err:
            self._logger.error("Step <create_extractor> fails with error: %s", str(err), exc_info=True)
            raise RuntimeError(err.args)

    def delete_document_type(self, data: CreateAzureExtractorSagaData) -> None:
        self._logger.debug("Starting <delete_document_type> step with data: %s", data.__dict__)
        try:
            self._document_type_proxy.delete_document_type(data.document_type_id)
            data.document_type_id = None

        except DocumentTypeProxyError as err:
            self._logger.error("Step <delete_document_type> fails with error: %s", str(err), exc_info=True)
            raise RuntimeError(err.args)

    def create_azure_extractor(self, data: CreateAzureExtractorSagaData) -> None:
        self._logger.debug("Starting <create_azure_extractor> step with data: %s", data.__dict__)
        try:
            self._azure_service.create_extractor(
                extractor_id=data.document_type_id,
                tenant_id=data.tenant_id,
                model_id=data.model_id,
                endpoint=data.endpoint,
                api_key=data.api_key,
            )
        except Exception as err:
            self._logger.error("Step <create_azure_extractor> fails with error: %s", str(err), exc_info=True)
            raise RuntimeError(err.args)

    def synchronize_azure_extractor(self, data: CreateAzureExtractorSagaData) -> None:
        self._logger.debug("Starting <synchronize_azure_extractor> step with data: %s", data.__dict__)
        try:
            self._azure_service.synchronize_extractor(
                data.document_type_id,
                data.tenant_id,
            )
        except Exception as err:
            self._logger.error("Step <synchronize_azure_extractor> fails with error: %s", str(err), exc_info=True)
            raise RuntimeError(err.args)

    def delete_extractor(self, data: CreateAzureExtractorSagaData) -> None:
        self._logger.debug("Starting <delete_extractor> step with data: %s", data.__dict__)
        try:
            self._azure_service.delete_extractor(data.document_type_id, data.tenant_id)

        except DocumentTypeProxyError as err:
            self._logger.error("Step <delete_extractor> fails with error: %s", str(err), exc_info=True)
            raise RuntimeError(err.args)
