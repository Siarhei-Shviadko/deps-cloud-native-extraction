from pydantic import Field

from ..base import ConfiguredBaseModel

__all__ = ["AzureExtractorInfoResponse"]


class AzureExtractorInfoResponse(ConfiguredBaseModel):
    id: str
    model_id: str = Field(..., alias="modelId")
    endpoint: str
