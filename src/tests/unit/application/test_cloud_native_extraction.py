from unittest.mock import MagicMock

from deps_cloud_native_extraction.application import CloudNativeExtractionApplication
from deps_cloud_native_extraction.domain.model import (
    AzureDIExtractor,
    CloudNativeExtractorTypes,
)
from deps_cloud_native_extraction.infrastructure.repositories import (
    AzureExtractorRepository,
)


def correct_infra_service_determined_for_extraction(
    mocked_azure_extraction_service: MagicMock,
    cloud_native_extraction_application: CloudNativeExtractionApplication,
) -> None:
    doc_id, tenant_id, extractor_id = "document_id", "tenant_id", "extractor_id"

    cloud_native_extraction_application.perform_extraction(
        document_id=doc_id,
        tenant_id=tenant_id,
        extractor_id=extractor_id,
        extractor_type=CloudNativeExtractorTypes.AZURE_CLOUD_EXTRACTOR,
    )

    mocked_azure_extraction_service.perform_extraction.assert_called_once_with(
        document_id=doc_id,
        tenant_id=tenant_id,
        extractor_id=extractor_id,
    )


def test_update_azure_extractor__updated(
    fake_azure_extractor_repository: AzureExtractorRepository,
    mocked_azure_extraction_service: MagicMock,
    cloud_native_extraction_application: CloudNativeExtractionApplication,
    test_saved_empty_azure_extractor: AzureDIExtractor,
):
    model_id, endpoint, api_key = "model_id", "endpoint", "api_key"
    cloud_native_extraction_application._azure_service = mocked_azure_extraction_service

    cloud_native_extraction_application.update_azure_extractor(
        extractor_id=test_saved_empty_azure_extractor.id(),
        tenant_id=test_saved_empty_azure_extractor.tenant_id(),
        model_id=model_id,
        endpoint=endpoint,
        api_key=api_key,
    )

    mocked_azure_extraction_service.update_extractor.assert_called_once_with(
        extractor_id=test_saved_empty_azure_extractor.id(),
        tenant_id=test_saved_empty_azure_extractor.tenant_id(),
        model_id=model_id,
        endpoint=endpoint,
        api_key=api_key,
    )
    mocked_azure_extraction_service.synchronize_extractor.assert_called_once_with(
        test_saved_empty_azure_extractor.id(),
        test_saved_empty_azure_extractor.tenant_id(),
    )

    mocked_azure_extraction_service.get_model_details.assert_called_once_with(
        endpoint=endpoint,
        model_id=model_id,
        api_key=api_key,
    )
