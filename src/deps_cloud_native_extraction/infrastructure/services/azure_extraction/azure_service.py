import logging
from datetime import datetime, timedelta
from uuid import uuid4

from azure.ai.documentintelligence.models import DocumentModelDetails
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
    ServiceRequestError,
)
from azure.keyvault.secrets import SecretClient
from deps_extracted_data import ExtractedData, ExtractedDataFactory
from deps_message_flow.events.publisher import DomainEventPublisher

from deps_cloud_native_extraction.domain.exceptions import (
    AuthError,
    AzureExtractorHttpClientError,
    AzureExtractorNotFoundError,
    NotFoundError,
)
from deps_cloud_native_extraction.domain.model import (
    AzureDIExtractor,
    AzureDIExtractorFactory,
    AzureDIField,
    FieldCode,
    IExtractorRepository,
)
from deps_cloud_native_extraction.domain.model.types import (
    RawAzureDIField,
    RawAzureDocumentType,
)
from deps_cloud_native_extraction.infrastructure.proxies import ExtractionProxy

from ..extractor_checkup_info import ExtractorCheckupInfo, ExtractorCheckupInfoFactory
from ..i_extract_documents import IExtractDocuments
from .azure_field_schema_parser import AzureFieldSchemaParser
from .client_factory import DIClientFactory
from .extraction_strategies.i_document_intelligence import (
    IDocumentIntelligenceExtractor,
)

__all__ = ["AzureExtractionService"]


class AzureExtractionService(IExtractDocuments):
    AGGREGATE_TYPE = "CloudNativeExtraction"
    VAULT_SECRET_KEY_POSTFIX = f"--{uuid4().hex[:4]}--api-key"
    MAX_KEY_VAULT_NAME_LENGTH = 111
    VAULT_KEYS_EXPIRATION_DAYS = 60

    def __init__(
        self,
        repository: IExtractorRepository,
        azure_key_vault_client: SecretClient,
        extraction_proxy: ExtractionProxy,
        document_intelligence_extractor: IDocumentIntelligenceExtractor,
        domain_event_publisher: DomainEventPublisher,
    ) -> None:
        self._repository = repository
        self._azure_key_vault_client = azure_key_vault_client
        self._extraction_proxy = extraction_proxy
        self._di_extractor = document_intelligence_extractor
        self._domain_event_publisher = domain_event_publisher

        self._logger = logging.getLogger(self.__class__.__name__)

    def perform_extraction(
        self,
        document_id: str,
        tenant_id: str,
        extractor_id: str,
    ) -> ExtractedData:
        if (azure_di_extractor := self._repository.get(extractor_id, tenant_id)) is None:
            raise AzureExtractorNotFoundError(f"We can't perform extraction, extractor with {extractor_id=} not found")

        api_key = self._get_api_key(
            name=azure_di_extractor.vault_key_name,
            version=azure_di_extractor.vault_key_version,
        )

        edata = ExtractedDataFactory.make_extracted_data(document_id=int(document_id))

        edata = self._di_extractor.extract(
            document_id=document_id,
            model_id=azure_di_extractor.model_id,
            data=edata,
            extractor_schema=azure_di_extractor.schema,
            extraction_client=DIClientFactory.for_endpoint(azure_di_extractor.endpoint).extraction_client_from_api_key(
                api_key,
            ),
            admin_client=DIClientFactory.for_endpoint(azure_di_extractor.endpoint).admin_client_from_api_key(api_key),
        )

        self._save_extracted_data(edata)

        return edata

    def create_extractor(
        self,
        extractor_id: str,
        tenant_id: str,
        model_id: str,
        endpoint: str,
        api_key: str,
    ) -> None:
        vault_key_id = self._save_api_key(tenant_id=tenant_id, model_id=model_id, api_key=api_key)

        extractor = AzureDIExtractorFactory.create_empty_extractor(
            _id=extractor_id,
            tenant_id=tenant_id,
            model_id=model_id,
            endpoint=endpoint,
            vault_key_id=vault_key_id,
        )

        self._repository.save(extractor)

    def update_extractor(
        self,
        extractor_id: str,
        tenant_id: str,
        model_id: str,
        endpoint: str,
        api_key: str,
    ) -> None:
        if (extractor := self._repository.get(extractor_id, tenant_id)) is None:
            raise AzureExtractorNotFoundError("Extractor not found.")

        vault_key_id = self._save_api_key(
            tenant_id=tenant_id,
            model_id=model_id,
            api_key=api_key,
        )

        extractor.update(model_id=model_id, endpoint=endpoint, vault_key_id=vault_key_id)

        self._repository.save(extractor)

    def synchronize_extractor(
        self,
        extractor_id: str,
        tenant_id: str,
    ) -> None:
        if extractor := self._repository.get(extractor_id, tenant_id):
            api_key = self._get_api_key(extractor.vault_key_name, extractor.vault_key_version)
            self._synchronize_fields_schema(extractor=extractor, api_key=api_key)
            return

        raise AzureExtractorNotFoundError("Extractor not found.")

    def delete_extractor(self, tenant_id: str, extractor_id: str) -> None:
        extractor = self._repository.get(id_=extractor_id, tenant_id=tenant_id)

        if extractor is None:
            return

        self._delete_api_key_for_extractor(extractor)
        self._repository.delete(id_=extractor_id, tenant_id=tenant_id)

    def get_model_details(self, endpoint: str, model_id: str, api_key: str) -> DocumentModelDetails:
        client = DIClientFactory.for_endpoint(endpoint).admin_client_from_api_key(api_key)
        try:
            return client.get_model(model_id)

        except (ServiceRequestError, ResourceNotFoundError) as err:
            self._logger.error(
                "Getting Azure Resource for endpoint: <%s>, model_id: <%s> fails. Error: %s",
                endpoint,
                model_id,
                str(err),
                exc_info=True,
            )

            raise NotFoundError("AzureResource not found.")

        except ClientAuthenticationError as err:
            self._logger.error("Azure client authentication error: %s", str(err), exc_info=True)
            raise AuthError("AzureClient authentication error.")

        except HttpResponseError as err:
            self._logger.error(
                "Getting Azure Resource for endpoint: <%s>, model_id: <%s> fails. Error: %s",
                endpoint,
                model_id,
                str(err),
                exc_info=True,
            )
            error_details = (
                f": {err.response.status_code} {err.response.reason}"
                if err.response is not None and (err.response.reason and err.response.status_code)
                else ""
            )
            raise AzureExtractorHttpClientError(f"AzureClient request to Azure failed with an error{error_details}")

    def extractor_checkup_info(self, extractor_id: str, tenant_id: str) -> ExtractorCheckupInfo:
        if (extractor := self._repository.get(extractor_id, tenant_id)) is None:
            raise AzureExtractorNotFoundError("Extractor not found.")

        api_key = self._get_api_key(extractor.vault_key_name, extractor.vault_key_version)
        try:
            doc_type = self._get_raw_azure_document_type(
                endpoint=extractor.endpoint,
                model_id=extractor.model_id,
                api_key=api_key,
            )

            return ExtractorCheckupInfoFactory.make_checkup_info(
                set(doc_type["field_schema"].keys()).difference(extractor.schema.keys()),
            )

        except AuthError as err:
            return ExtractorCheckupInfoFactory.make_api_key_expired_checkup_info(err.args)

        except Exception as err:
            self._logger.error("Unexpected error ocurred. Error: %s", str(err), exc_info=True)
            return ExtractorCheckupInfoFactory.make_error_checup_info(err.args)

    def _create_vault_key_name(self, tenant_id: str, model_id: str) -> str:
        sanitized_model_id = "".join(char if char.isalnum() or char == "-" else "-" for char in model_id)
        sanitized_tenant_id = "".join(char if char.isalnum() or char == "-" else "-" for char in tenant_id)
        name = f"{sanitized_tenant_id}--{sanitized_model_id}"

        return name[: self.MAX_KEY_VAULT_NAME_LENGTH] + self.VAULT_SECRET_KEY_POSTFIX

    def _save_extracted_data(self, extracted_data: ExtractedData) -> None:
        self._extraction_proxy.save_extracted_data(extracted_data=extracted_data)

    def _synchronize_fields_schema(self, extractor: AzureDIExtractor, api_key: str) -> None:
        doc_type = self._get_raw_azure_document_type(
            endpoint=extractor.endpoint,
            model_id=extractor.model_id,
            api_key=api_key,
        )
        extractor.track_schema_updates(doc_type)
        self._publish_events(extractor)
        self._repository.save(extractor)

    def _get_raw_azure_document_type(self, endpoint: str, model_id: str, api_key: str) -> RawAzureDocumentType:
        model_details = self.get_model_details(
            endpoint=endpoint,
            model_id=model_id,
            api_key=api_key,
        )

        return AzureFieldSchemaParser(model_id, model_details).parse()

    def _save_api_key(self, tenant_id: str, model_id: str, api_key: str) -> str:
        try:
            response = self._azure_key_vault_client.set_secret(
                name=self._create_vault_key_name(tenant_id, model_id),
                value=api_key,
                expires_on=datetime.now() + timedelta(days=self.VAULT_KEYS_EXPIRATION_DAYS),
            )

            return response.id
        except HttpResponseError as err:
            self._logger.error("Saving api-key in azure key vault fails with error: %s", str(err), exc_info=True)
            raise

    def _get_api_key(self, name: str, version: str) -> str:
        try:
            return self._azure_key_vault_client.get_secret(name=name, version=version).value
        except HttpResponseError as err:
            self._logger.error("Getting api_key from azure key vault fails with error: %s", str(err), exc_info=True)
            raise

    def _delete_api_key_for_extractor(self, extractor: AzureDIExtractor) -> None:
        try:
            self._azure_key_vault_client.begin_delete_secret(extractor.vault_key_name)
        except HttpResponseError as err:
            self._logger.error("Deleting api-key in azure key vault fails with error: %s", str(err), exc_info=True)
            raise

    def _publish_events(self, extractor: AzureDIExtractor) -> None:
        self._domain_event_publisher.publish(
            self.AGGREGATE_TYPE,
            str(extractor.id),
            extractor.events,
        )
