from azure.ai.documentintelligence import (
    DocumentIntelligenceAdministrationClient,
    DocumentIntelligenceClient,
)
from azure.core.credentials import AzureKeyCredential

__all__ = ["DIClientFactory"]


class DIClientFactory:
    def __init__(self, endpoint: str) -> None:
        self._endpoint = endpoint.rstrip("/") if endpoint else endpoint

    @classmethod
    def for_endpoint(cls, endpoint: str) -> "DIClientFactory":
        return cls(endpoint=endpoint)

    def extraction_client_from_api_key(self, key: str) -> DocumentIntelligenceClient:
        return DocumentIntelligenceClient(
            endpoint=self._endpoint,
            credential=AzureKeyCredential(key),
        )

    def admin_client_from_api_key(self, key: str) -> DocumentIntelligenceAdministrationClient:
        return DocumentIntelligenceAdministrationClient(
            endpoint=self._endpoint,
            credential=AzureKeyCredential(key),
        )
