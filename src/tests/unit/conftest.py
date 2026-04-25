from typing import Any
from uuid import uuid4

import pytest

from deps_cloud_native_extraction.domain.model import (
    AzureDIExtractor,
    AzureDIExtractorFactory,
)
from deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_field_schema_parser import (
    AzureFieldSchemaParser,
)
from tests.fakes import FakeAzureExtractorRepository, FakeUnitOfWork


@pytest.fixture
def postgres_session_mock(mocker, containers):
    mock = mocker.Mock(containers.datasources.postgres_session())
    containers.datasources.postgres_session.override(mock)

    yield mock

    containers.datasources.postgres_session.reset_override()


@pytest.fixture(autouse=True, scope="function")
def fake_unit_of_work(containers):
    fuow = FakeUnitOfWork()

    containers.unit_of_work.override(fuow)

    yield fuow

    containers.unit_of_work.reset_override()


@pytest.fixture
def fake_azure_extractor_repository(repositories):
    with repositories.azure_extractor.override(FakeAzureExtractorRepository()) as repo:
        yield repo()


@pytest.fixture(autouse=True)
def mocked_azure_secret_client(containers, mocker):
    mock = mocker.Mock(containers.clients.azure_key_vault.cls)
    with containers.clients.azure_key_vault.override(mock) as mocked:
        yield mocked()


@pytest.fixture
def mocked_azure_extraction_service(containers, mocker):
    mock = mocker.Mock(containers.services.azure.cls)
    with containers.services.azure.override(mock) as mocked:
        yield mocked()


@pytest.fixture
def cloud_native_extraction_application(containers):
    return containers.applications.cloud_native_extraction()


@pytest.fixture
def test_saved_empty_azure_extractor(
    fake_azure_extractor_repository,
    test_tenant,
    test_endpoint,
    test_model_id,
    test_azure_vault_key_id,
) -> AzureDIExtractor:
    extractor = AzureDIExtractorFactory.create_empty_extractor(
        _id=uuid4().hex,
        tenant_id=test_tenant,
        endpoint=test_endpoint,
        model_id=test_model_id,
        vault_key_id=test_azure_vault_key_id,
    )
    fake_azure_extractor_repository.save(extractor)

    return extractor


@pytest.fixture
def test_model_schema(test_saved_empty_azure_extractor) -> dict[str, Any]:
    return {
        "docTypes": {
            test_saved_empty_azure_extractor.model_id: {
                "fieldSchema": {
                    "result": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ROW1": {"type": "string"},
                                "ROW2": {"type": "string"},
                                "ROW3": {"type": "string"},
                                "ROW4": {"type": "string"},
                                "ROW5": {"type": "string"},
                            },
                        },
                    },
                    "Category-string": {"type": "string"},
                    "sheet-checkmark": {"type": "selectionMark"},
                    "results-table": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {"COLUMN1": {"type": "string"}, "COLUMN2": {"type": "string"}},
                        },
                    },
                    "year": {"type": "number"},
                    "date": {"type": "date"},
                    "time": {"type": "time"},
                    "order": {"type": "integer"},
                },
                "buildMode": "neural",
            },
        },
        "trainingHours": 0.5,
        "modelId": test_saved_empty_azure_extractor.model_id,
        "createdDateTime": "2025-03-05T15:16:55Z",
        "modifiedDateTime": "2025-03-05T15:16:55Z",
        "expirationDateTime": "2027-03-05T15:16:55Z",
        "apiVersion": "2024-11-30",
        "description": "test_azure_extractor_with_fields",
    }


@pytest.fixture
def test_saved_azure_extractor_with_schema(test_saved_empty_azure_extractor, test_model_schema):
    test_saved_empty_azure_extractor.track_schema_updates(
        AzureFieldSchemaParser(test_saved_empty_azure_extractor.model_id, test_model_schema).parse(),
    )
    return test_saved_empty_azure_extractor
