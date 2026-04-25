from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from deps_cloud_native_extraction import api
from deps_cloud_native_extraction.entrypoint import create_fastapi
from deps_cloud_native_extraction.infrastructure.access_management.context_vars import (
    user,
)


@pytest.fixture(scope="session")
def app() -> FastAPI:
    fastapi_app = create_fastapi()

    yield fastapi_app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def session_containers(app):
    return app.containers


@pytest.fixture
def containers(session_containers):
    with session_containers.reset_singletons():
        yield session_containers


@pytest.fixture(autouse=True)
def domain_event_publisher_mock(containers):
    mock = Mock(containers.domain_event_publisher())

    with containers.domain_event_publisher.override(mock) as dep:
        yield dep()


@pytest.fixture
def repositories(containers):
    return containers.repositories


@pytest.fixture
def test_tenant():
    return uuid4().hex


@pytest.fixture
def this_user(test_tenant):
    return dict(
        subject="PinkKey",
        groups=[test_tenant],
        token="token",
        roles=["doctor"],
        organisation=test_tenant,
    )


@pytest.fixture(autouse=True)
def set_this_user(this_user):
    user.set(this_user)


@pytest.fixture(autouse=True)
def mocked_middleware(monkeypatch, mocker):
    monkeypatch.setattr(api.auth, "set_user_from_token", mocker.Mock({}))


@pytest.fixture
def test_code():
    return uuid4().hex


@pytest.fixture
def test_column_name():
    return uuid4().hex


@pytest.fixture
def test_endpoint():
    return f"https://{uuid4().hex}.cognitiveservices.azure.com/"


@pytest.fixture
def test_model_id():
    return uuid4().hex


@pytest.fixture
def test_azure_api_key():
    return uuid4().hex


@pytest.fixture
def test_azure_vault_key_id():
    return f"https://{uuid4().hex}.vault.azure.net/secrets/{uuid4().hex}/{uuid4().hex}"
