from typing import Any

import pytest


@pytest.fixture
def test_azure_extraction_service(mocked_azure_secret_client, containers):
    containers.reset_singletons()
    service = containers.services.azure()
    service._azure_key_vault_client = mocked_azure_secret_client

    yield service
