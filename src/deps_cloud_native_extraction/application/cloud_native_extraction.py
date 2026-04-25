import logging
from typing import Optional

from deps_message_flow.sagas.orchestration import Saga, SagaInstanceFactory

from deps_cloud_native_extraction.domain.exceptions import (
    AuthError,
    AzureExtractorError,
    AzureExtractorInvalidCredentialsError,
    AzureExtractorNotFoundError,
    NotFoundError,
)
from deps_cloud_native_extraction.domain.model import (
    AzureExtractorInfo,
    CloudNativeExtractorTypes,
    IExtractorRepository,
)
from deps_cloud_native_extraction.infrastructure.services import (
    AzureExtractionService,
    IExtractDocuments,
)
from deps_cloud_native_extraction.infrastructure.services.extractor_checkup_info import (
    ExtractorCheckupInfo,
)
from deps_cloud_native_extraction.messaging.sagas import (
    CreateAzureExtractorSaga,
    CreateAzureExtractorSagaData,
)

__all__ = ["CloudNativeExtractionApplication"]


class CloudNativeExtractionApplication:
    def __init__(
        self,
        azure_service: AzureExtractionService,
        azure_repository: IExtractorRepository,
        sagas: list[Saga],
        saga_instance_factory: SagaInstanceFactory,
    ) -> None:
        self._azure_service = azure_service
        self._azure_repository = azure_repository

        self._extraction_services_mapping: dict[CloudNativeExtractorTypes, IExtractDocuments] = {
            CloudNativeExtractorTypes.AZURE_CLOUD_EXTRACTOR: self._azure_service,
        }
        self._extraction_repositories_mapping: dict[CloudNativeExtractorTypes, IExtractorRepository] = {
            CloudNativeExtractorTypes.AZURE_CLOUD_EXTRACTOR: self._azure_repository,
        }

        self._sagas = {saga.__class__: saga for saga in sagas}
        self._saga_instance_factory = saga_instance_factory

        self._logger = logging.getLogger(self.__class__.__name__)

    def perform_extraction(
        self,
        document_id: str,
        tenant_id: str,
        extractor_id: str,
        extractor_type: CloudNativeExtractorTypes,
    ) -> None:
        self._extraction_services_mapping[extractor_type].perform_extraction(
            document_id=document_id,
            tenant_id=tenant_id,
            extractor_id=extractor_id,
        )

    def create_azure_extractor(
        self,
        name: str,
        tenant_id: str,
        model_id: str,
        endpoint: str,
        api_key: str,
        language: Optional[str],
        description: Optional[str],
    ) -> str:
        self._logger.info(
            "Starting CreateAzureExtractorSaga with name: %s, tenant_id: %s, model_id: %s, endpoint: %s",
            name,
            tenant_id,
            model_id,
            endpoint,
        )

        saga_data = CreateAzureExtractorSagaData(
            name=name,
            tenant_id=tenant_id,
            model_id=model_id,
            endpoint=endpoint,
            api_key=api_key,
            language=language,
            description=description,
        )
        self._saga_instance_factory.create(
            saga=self._sagas[CreateAzureExtractorSaga],
            data=saga_data,
        )

        if document_type_id := saga_data.document_type_id:
            return document_type_id

        raise AzureExtractorError("Can't create AzureExtractor")

    def update_azure_extractor(
        self,
        extractor_id: str,
        tenant_id: str,
        model_id: str,
        endpoint: str,
        api_key: str,
    ) -> None:
        self.validate_azure_credentials(endpoint=endpoint, model_id=model_id, api_key=api_key)

        self._azure_service.update_extractor(
            extractor_id=extractor_id,
            tenant_id=tenant_id,
            model_id=model_id,
            endpoint=endpoint,
            api_key=api_key,
        )

        self.synchronize_azure_extractor(extractor_id=extractor_id, tenant_id=tenant_id)

    def synchronize_azure_extractor(self, extractor_id: str, tenant_id: str) -> None:
        self._azure_service.synchronize_extractor(extractor_id, tenant_id)

    def get_azure_extractor_info(self, extractor_id: str, tenant_id: str) -> AzureExtractorInfo:
        if extractor_info := self._azure_repository.get_extractor_info(extractor_id, tenant_id):
            return extractor_info

        raise AzureExtractorNotFoundError

    def validate_azure_credentials(self, endpoint: str, model_id: str, api_key: str) -> None:
        try:
            self._azure_service.get_model_details(endpoint=endpoint, model_id=model_id, api_key=api_key)
        except (AuthError, NotFoundError) as err:
            raise AzureExtractorInvalidCredentialsError(", ".join(err.args))

    def azure_checkup(self, extractor_id: str, tenant_id: str) -> ExtractorCheckupInfo:
        return self._azure_service.extractor_checkup_info(extractor_id=extractor_id, tenant_id=tenant_id)

    def delete_extractor_field(
        self,
        extractor_id: str,
        tenant_id: str,
        field_code: str,
        extractor_type: str,
    ) -> None:
        try:
            repository = self._extraction_repositories_mapping[CloudNativeExtractorTypes(extractor_type)]
            if extractor := repository.get(id_=extractor_id, tenant_id=tenant_id):
                extractor.delete_field(field_code)
                repository.save(extractor)

        except ValueError as err:
            self._logger.debug("I can't remove field belongs to %s type. Error: %s", extractor_type, str(err))
