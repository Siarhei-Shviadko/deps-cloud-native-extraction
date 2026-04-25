from collections import namedtuple
from http import HTTPStatus
from unittest import mock

import pytest
from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient
from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceNotFoundError,
    ServiceRequestError,
)

from deps_cloud_native_extraction import constants
from deps_cloud_native_extraction.domain.exceptions import AzureExtractorNotFoundError
from deps_cloud_native_extraction.infrastructure.services.extractor_checkup_info import (
    ExtractorStatus,
)

KeyVaultSecret = namedtuple("KeyVaultSecret", ["value"])


@pytest.mark.usefixtures("fake_azure_extractor_repository")
class TestAzure:
    endpoint = f"{constants.V1_API_PREFIX}/azure"

    def test_get_azure_extractor_info_extractor_doesnt_exist__404(self, client):
        response = client.get(f"{self.endpoint}/extractor/fake-id")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_azure_extractor_info_extractor_extractor_exists__200(
        self,
        client,
        test_saved_empty_azure_extractor,
    ):
        response = client.get(f"{self.endpoint}/extractor/{test_saved_empty_azure_extractor.id()}")

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert response_json["id"] == test_saved_empty_azure_extractor.id()
        assert response_json["modelId"] == test_saved_empty_azure_extractor.model_id
        assert response_json["endpoint"] == test_saved_empty_azure_extractor.endpoint

    @mock.patch(
        "deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_service.DIClientFactory",
    )
    def test_validate_credentials__ok(self, mocked_admin_client_factory, client, test_model_schema):
        mocked_client = mock.MagicMock(spec=DocumentIntelligenceAdministrationClient)
        mocked_client.get_model.return_value = test_model_schema
        mocked_factory_inst = mock.MagicMock()
        mocked_factory_inst.admin_client_from_api_key.return_value = mocked_client
        mocked_admin_client_factory.for_endpoint.return_value = mocked_factory_inst

        response = client.post(
            f"{self.endpoint}/validate-credentials",
            json={"endpoint": "my_endpoint", "modelId": "model_id", "apiKey": "my_api_key"},
        )

        assert response.status_code == HTTPStatus.OK

    @mock.patch(
        "deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_service.DIClientFactory",
    )
    def test_validate_credentials__ok__endpoint_with_slash(
        self, mocked_admin_client_factory, client, test_model_schema
    ):
        mocked_client = mock.MagicMock(spec=DocumentIntelligenceAdministrationClient)
        mocked_client.get_model.return_value = test_model_schema
        mocked_factory_inst = mock.MagicMock()
        mocked_factory_inst.admin_client_from_api_key.return_value = mocked_client
        mocked_admin_client_factory.for_endpoint.return_value = mocked_factory_inst

        response = client.post(
            f"{self.endpoint}/validate-credentials",
            json={"endpoint": "my_endpoint/", "modelId": "model_id", "apiKey": "my_api_key"},
        )

        assert response.status_code == HTTPStatus.OK

        mocked_admin_client_factory.for_endpoint.assert_called_once_with("my_endpoint")

    @mock.patch(
        "deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_service.DIClientFactory",
    )
    def test_validate_credentials__error__400(self, mocked_admin_client_factory, client):
        mocked_client = mock.MagicMock(spec=DocumentIntelligenceAdministrationClient)
        mocked_client.get_model.side_effect = [
            ServiceRequestError("Bad url"),
            ResourceNotFoundError("Resource not found"),
            ClientAuthenticationError("Authentication error"),
        ]
        mocked_factory_inst = mock.MagicMock()
        mocked_factory_inst.admin_client_from_api_key.return_value = mocked_client
        mocked_admin_client_factory.for_endpoint.return_value = mocked_factory_inst

        response = client.post(
            f"{self.endpoint}/validate-credentials",
            json={"endpoint": "unreal_url", "modelId": "model_id", "apiKey": "my_api_key"},
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

        response2 = client.post(
            f"{self.endpoint}/validate-credentials",
            json={"endpoint": "my_endpoint", "modelId": "bad_model_id", "apiKey": "my_api_key"},
        )

        assert response2.status_code == HTTPStatus.BAD_REQUEST

        response3 = client.post(
            f"{self.endpoint}/validate-credentials",
            json={"endpoint": "my_endpoint", "modelId": "model_id", "apiKey": "bad_api_key"},
        )

        assert response3.status_code == HTTPStatus.BAD_REQUEST

    def test_checkup__no_extractor__404_error(
        self,
        client,
        test_saved_empty_azure_extractor,
    ):
        response = client.get("{self.endpoint}/extractor/fake_id/checkup")

        assert response.status_code == HTTPStatus.NOT_FOUND

    @mock.patch(
        "deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_service.DIClientFactory",
    )
    def test_checkup__extractor_not_synchronized__ok(
        self,
        mocked_admin_client_factory,
        mocked_azure_secret_client,
        client,
        test_model_schema,
        test_azure_api_key,
        test_saved_empty_azure_extractor,
    ):
        mocked_client = mock.MagicMock(spec=DocumentIntelligenceAdministrationClient)
        mocked_client.get_model.return_value = test_model_schema

        mocked_factory_inst = mock.MagicMock()
        mocked_factory_inst.admin_client_from_api_key.return_value = mocked_client
        mocked_admin_client_factory.for_endpoint.return_value = mocked_factory_inst

        mocked_azure_secret_client.get_secret.return_value = KeyVaultSecret(test_azure_api_key)
        response = client.get(f"{self.endpoint}/extractor/{test_saved_empty_azure_extractor.id()}/checkup")

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert response_json["status"] == ExtractorStatus.UNSYNCHRONIZED

    @mock.patch(
        "deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_service.DIClientFactory",
    )
    def test_checkup__extractor_synchronized__ok(
        self,
        mocked_admin_client_factory,
        mocked_azure_secret_client,
        client,
        test_model_schema,
        test_azure_api_key,
        test_saved_azure_extractor_with_schema,
    ):
        mocked_client = mock.MagicMock(spec=DocumentIntelligenceAdministrationClient)
        mocked_client.get_model.return_value = test_model_schema

        mocked_factory_inst = mock.MagicMock()
        mocked_factory_inst.admin_client_from_api_key.return_value = mocked_client
        mocked_admin_client_factory.for_endpoint.return_value = mocked_factory_inst

        mocked_azure_secret_client.get_secret.return_value = KeyVaultSecret(test_azure_api_key)
        response = client.get(f"{self.endpoint}/extractor/{test_saved_azure_extractor_with_schema.id()}/checkup")

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert response_json["status"] == ExtractorStatus.SYNCHRONIZED

    @mock.patch(
        "deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_service.DIClientFactory",
    )
    def test_checkup__api_key_expired__ok(
        self,
        mocked_admin_client_factory,
        mocked_azure_secret_client,
        client,
        test_azure_api_key,
        test_saved_azure_extractor_with_schema,
    ):
        mocked_client = mock.MagicMock(spec=DocumentIntelligenceAdministrationClient)
        mocked_client.get_model.side_effect = ClientAuthenticationError("API Key is expired test message")  # TODO: ???

        mocked_factory_inst = mock.MagicMock()
        mocked_factory_inst.admin_client_from_api_key.return_value = mocked_client
        mocked_admin_client_factory.for_endpoint.return_value = mocked_factory_inst

        mocked_azure_secret_client.get_secret.return_value = KeyVaultSecret(test_azure_api_key)
        response = client.get(f"{self.endpoint}/extractor/{test_saved_azure_extractor_with_schema.id()}/checkup")

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert response_json["status"] == ExtractorStatus.API_KEY_EXPIRED

    @mock.patch(
        "deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_service.DIClientFactory",
    )
    def test_checkup__error_occured__ok(
        self,
        mocked_admin_client_factory,
        mocked_azure_secret_client,
        client,
        test_azure_api_key,
        test_saved_azure_extractor_with_schema,
    ):
        mocked_client = mock.MagicMock(spec=DocumentIntelligenceAdministrationClient)
        mocked_client.get_model.side_effect = RuntimeError("Unexpected error")

        mocked_factory_inst = mock.MagicMock()
        mocked_factory_inst.admin_client_from_api_key.return_value = mocked_client
        mocked_admin_client_factory.for_endpoint.return_value = mocked_factory_inst

        mocked_azure_secret_client.get_secret.return_value = KeyVaultSecret(test_azure_api_key)
        response = client.get(f"{self.endpoint}/extractor/{test_saved_azure_extractor_with_schema.id()}/checkup")

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert response_json["status"] == ExtractorStatus.ERROR
        assert "Unexpected error" in response_json["description"]

    def test_synchronize__ok(
        self,
        client,
        mocked_azure_extraction_service,
        test_saved_empty_azure_extractor,
    ):
        response = client.put(f"{self.endpoint}/extractor/{test_saved_empty_azure_extractor.id()}/synchronize")

        assert response.status_code == HTTPStatus.OK

    def test_synchronize__no_extractor__404(
        self,
        client,
        mocked_azure_extraction_service,
    ):
        mocked_azure_extraction_service.synchronize_extractor.side_effect = AzureExtractorNotFoundError
        response = client.put(f"{self.endpoint}/extractor/fake_id/synchronize")

        assert response.status_code == HTTPStatus.NOT_FOUND
