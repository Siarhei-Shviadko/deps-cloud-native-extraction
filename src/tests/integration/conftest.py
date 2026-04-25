from uuid import uuid4

import pytest

from deps_cloud_native_extraction.application import CloudNativeExtractionApplication
from deps_cloud_native_extraction.domain.model import (
    AzureDIExtractor,
    AzureDIExtractorFactory,
    AzureDIField,
    AzureDIFieldType,
)
from deps_cloud_native_extraction.infrastructure.repositories import (
    AzureExtractorRepository,
)
from tests.factories.azure_extractor import AzureFieldFactory


@pytest.fixture
def unit_of_work(containers):
    return containers.unit_of_work()


@pytest.fixture
def azure_extractor_repository(repositories) -> AzureExtractorRepository:
    return repositories.azure_extractor()


@pytest.fixture
def cloud_native_extraction_app(containers) -> CloudNativeExtractionApplication:
    return containers.applications.cloud_native_extraction()


@pytest.fixture
def azure_extractor_string_field() -> AzureDIField:
    return AzureFieldFactory(_type=AzureDIFieldType.STRING)


@pytest.fixture
def azure_extractor_table_field() -> AzureDIField:
    return AzureFieldFactory(_type=AzureDIFieldType.TABLE)


@pytest.fixture
def azure_extractor(
    test_tenant: str,
    test_endpoint: str,
    test_model_id: str,
    test_azure_vault_key_id: str,
    azure_extractor_string_field: AzureDIField,
    azure_extractor_table_field: AzureDIField,
) -> AzureDIExtractor:
    extractor = AzureDIExtractorFactory.create_empty_extractor(
        _id=uuid4().hex,
        tenant_id=test_tenant,
        endpoint=test_endpoint,
        model_id=test_model_id,
        vault_key_id=test_azure_vault_key_id,
    )
    extractor.schema = {
        azure_extractor_string_field.code(): azure_extractor_string_field,
        azure_extractor_table_field.code(): azure_extractor_table_field,
    }

    return extractor


@pytest.fixture
def saved_azure_extractor(azure_extractor, azure_extractor_repository) -> AzureDIExtractor:
    azure_extractor_repository.save(azure_extractor)
    return azure_extractor
