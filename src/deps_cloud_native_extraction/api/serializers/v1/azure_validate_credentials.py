from pydantic import Field, field_validator

from ..base import ConfiguredBaseModel

__all__ = ["ValidateAzureCredentialsRequest"]


class ValidateAzureCredentialsRequest(ConfiguredBaseModel):
    endpoint: str
    model_id: str = Field(..., alias="modelId", min_length=1)
    api_key: str = Field(..., alias="apiKey")

    @field_validator("endpoint", mode="before")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/") if isinstance(v, str) else v
