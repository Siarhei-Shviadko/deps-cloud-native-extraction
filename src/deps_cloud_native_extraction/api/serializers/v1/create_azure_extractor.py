from typing import Optional

from pydantic import Field, field_validator

from ..base import ConfiguredBaseModel

__all__ = ["CreateAzureExtractorRequest", "CreateAzureExtractorResponse"]


class CreateAzureExtractorRequest(ConfiguredBaseModel):
    name: str
    model_id: str = Field(..., alias="modelId", min_length=1)
    endpoint: str
    api_key: str = Field(..., alias="apiKey")
    language: Optional[str] = None
    description: Optional[str] = None

    @field_validator("endpoint", mode="before")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/") if isinstance(v, str) else v


class CreateAzureExtractorResponse(ConfiguredBaseModel):
    extractor_id: str = Field(..., alias="extractorId")

    @classmethod
    def from_document_type_id(cls, document_type_id: str) -> "CreateAzureExtractorResponse":
        return cls(extractor_id=document_type_id)
