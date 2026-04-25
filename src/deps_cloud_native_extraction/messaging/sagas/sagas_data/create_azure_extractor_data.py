from typing import Optional
from uuid import uuid4

from deps_message_flow.sagas.orchestration import SagaData

__all__ = ["CreateAzureExtractorSagaData"]


class CreateAzureExtractorSagaData(SagaData):
    def __init__(
        self,
        name: str,
        tenant_id: str,
        model_id: str,
        endpoint: str,
        api_key: str,
        language: Optional[str],
        description: Optional[str],
    ):
        super().__init__(entity_id=uuid4().hex)
        self.name = name
        self.tenant_id = tenant_id
        self.model_id = model_id
        self.endpoint = endpoint
        self.api_key = api_key
        self.language = language
        self.description = description

        self.document_type_id: Optional[str] = None
