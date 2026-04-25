from typing import TypedDict

from ..azure_extractor.azure_field_type import AzureDIFieldType

__all__ = [
    "RawAzureDocumentType",
    "RawAzureDIField",
    "RawTableDescription",
    "RawAzureColumn",
]


class RawAzureColumn(TypedDict):
    name: str
    type: AzureDIFieldType


class RawTableDescription(TypedDict):
    columns: list[RawAzureColumn]


class RawAzureDIField(TypedDict):
    code: str
    type: AzureDIFieldType
    description: RawTableDescription | None


class RawAzureDocumentType(TypedDict):
    field_schema: dict[str, RawAzureDIField]
