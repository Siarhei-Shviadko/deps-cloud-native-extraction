from collections import namedtuple
from unittest import mock

import pytest
from azure.keyvault.secrets import SecretClient

from deps_cloud_native_extraction.domain.events import (
    CloudExtractorFieldCreated,
    CloudExtractorFieldDeleted,
    CloudExtractorFieldUpdated,
)
from deps_cloud_native_extraction.domain.exceptions import (
    AzureExtractorNotFoundError,
    ChangeTypeError,
    NotFoundError,
)
from deps_cloud_native_extraction.domain.model import (
    AzureDIExtractor,
    IExtractorRepository,
)
from deps_cloud_native_extraction.infrastructure.services import AzureExtractionService

KeyVaultSecret = namedtuple("KeyVaultSecret", ["value"])


def test_synchronize_azure_extractor__extractor_doesnt_exist__error(
    fake_azure_extractor_repository,
    test_azure_extraction_service,
    test_tenant,
):
    with pytest.raises(NotFoundError):
        test_azure_extraction_service.synchronize_extractor(extractor_id="fake_id", tenant_id=test_tenant)


@mock.patch(
    "deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_service.DIClientFactory",
)
def test_synchronize_azure_extractor_firstly__all_fields_added(
    mocked_admin_client_factory,
    test_model_schema,
    mocked_azure_secret_client,
    test_saved_empty_azure_extractor,
    test_azure_extraction_service,
    test_tenant,
    test_azure_api_key,
):
    mocked_admin_client = mock.MagicMock()
    mocked_admin_client.get_model.return_value = test_model_schema

    mocked_admin_client_factory_ = mock.MagicMock()
    mocked_admin_client_factory_.admin_client_from_api_key.return_value = mocked_admin_client

    mocked_admin_client_factory.for_endpoint.return_value = mocked_admin_client_factory_

    mocked_azure_secret_client.get_secret.return_value = KeyVaultSecret(test_azure_api_key)

    test_azure_extraction_service.synchronize_extractor(
        extractor_id=test_saved_empty_azure_extractor.id(),
        tenant_id=test_tenant,
    )

    field_created_events = [
        event for event in test_saved_empty_azure_extractor._events if isinstance(event, CloudExtractorFieldCreated)
    ]
    assert len(field_created_events) == 8


@mock.patch(
    "deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_service.DIClientFactory",
)
def test_synchronize_azure_extractor_secondly__field_type_changed__error(
    mocked_admin_client_factory,
    test_model_schema,
    mocked_azure_secret_client,
    test_saved_empty_azure_extractor,
    test_azure_extraction_service,
    test_tenant,
    test_azure_api_key,
):
    mocked_admin_client = mock.MagicMock()
    mocked_admin_client.get_model.return_value = test_model_schema

    mocked_admin_client_factory_ = mock.MagicMock()
    mocked_admin_client_factory_.admin_client_from_api_key.return_value = mocked_admin_client

    mocked_admin_client_factory.for_endpoint.return_value = mocked_admin_client_factory_

    mocked_azure_secret_client.get_secret.return_value = KeyVaultSecret(test_azure_api_key)

    mocked_admin_client.return_value.get_model.return_value = test_model_schema

    test_azure_extraction_service.synchronize_extractor(
        extractor_id=test_saved_empty_azure_extractor.id(),
        tenant_id=test_tenant,
    )
    test_model_schema["docTypes"][test_saved_empty_azure_extractor.model_id]["fieldSchema"]["year"]["type"] = "string"

    with pytest.raises(ChangeTypeError):
        test_azure_extraction_service.synchronize_extractor(
            extractor_id=test_saved_empty_azure_extractor.id(),
            tenant_id=test_tenant,
        )


@mock.patch(
    "deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_service.DIClientFactory",
)
def test_synchronize_azure_extractor_secondly__schema_changed__all_changes_applied(
    mocked_admin_client_factory,
    test_model_schema,
    mocked_azure_secret_client,
    test_saved_empty_azure_extractor,
    test_azure_extraction_service,
    test_tenant,
    test_azure_api_key,
):
    mocked_admin_client = mock.MagicMock()
    mocked_admin_client.get_model.return_value = test_model_schema

    mocked_admin_client_factory_ = mock.MagicMock()
    mocked_admin_client_factory_.admin_client_from_api_key.return_value = mocked_admin_client

    mocked_admin_client_factory.for_endpoint.return_value = mocked_admin_client_factory_

    mocked_azure_secret_client.get_secret.return_value = KeyVaultSecret(test_azure_api_key)

    mocked_admin_client.return_value.get_model.return_value = test_model_schema

    test_azure_extraction_service.synchronize_extractor(
        extractor_id=test_saved_empty_azure_extractor.id(),
        tenant_id=test_tenant,
    )

    field = test_model_schema["docTypes"][test_saved_empty_azure_extractor.model_id]["fieldSchema"].pop("date")
    test_model_schema["docTypes"][test_saved_empty_azure_extractor.model_id]["fieldSchema"]["new_date"] = field

    cell = test_model_schema["docTypes"][test_saved_empty_azure_extractor.model_id]["fieldSchema"]["result"]["items"][
        "properties"
    ].pop("ROW2")
    test_model_schema["docTypes"][test_saved_empty_azure_extractor.model_id]["fieldSchema"]["result"]["items"][
        "properties"
    ]["CHANGED_CELL_NAME"] = cell

    test_saved_empty_azure_extractor._events.clear()

    test_azure_extraction_service.synchronize_extractor(
        extractor_id=test_saved_empty_azure_extractor.id(),
        tenant_id=test_tenant,
    )

    field_created_events = [
        event for event in test_saved_empty_azure_extractor._events if isinstance(event, CloudExtractorFieldCreated)
    ]

    field_updated_events = [
        event for event in test_saved_empty_azure_extractor._events if isinstance(event, CloudExtractorFieldUpdated)
    ]

    field_deleted_events = [
        event for event in test_saved_empty_azure_extractor._events if isinstance(event, CloudExtractorFieldDeleted)
    ]

    assert len(field_created_events) == 1
    assert len(field_updated_events) == 1
    assert len(field_deleted_events) == 1

    assert test_saved_empty_azure_extractor.schema["new_date"]
    assert test_saved_empty_azure_extractor.schema["result"].description.columns["CHANGED_CELL_NAME"]
    assert "date" not in test_saved_empty_azure_extractor.schema


def test_delete_azure_extractor__success(
    fake_azure_extractor_repository: IExtractorRepository,
    test_azure_extraction_service: AzureExtractionService,
    test_saved_empty_azure_extractor: AzureDIExtractor,
    mocked_azure_secret_client: SecretClient,
    test_tenant: str,
    mocker,
):
    mocked_azure_secret_client.begin_delete_secret = mocker.Mock()

    test_azure_extraction_service.delete_extractor(
        extractor_id=test_saved_empty_azure_extractor.id(),
        tenant_id=test_tenant,
    )

    assert fake_azure_extractor_repository.get(id_=test_saved_empty_azure_extractor.id(), tenant_id=test_tenant) is None
    mocked_azure_secret_client.begin_delete_secret.assert_called_once_with(
        test_saved_empty_azure_extractor.vault_key_name,
    )


def test_perform_extraction__extractor_doesnt_exist__error(
    fake_azure_extractor_repository: IExtractorRepository,
    test_azure_extraction_service: AzureExtractionService,
    test_tenant: str,
):
    with pytest.raises(AzureExtractorNotFoundError):
        test_azure_extraction_service.perform_extraction(
            document_id="fake_id",
            tenant_id=test_tenant,
            extractor_id="fake_id",
        )
