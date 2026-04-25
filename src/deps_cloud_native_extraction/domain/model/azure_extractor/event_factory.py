from typing import Optional

from ...events import (
    CloudExtractorFieldCreated,
    CloudExtractorFieldDeleted,
    CloudExtractorFieldUpdated,
)
from ..types import FieldDescription
from .azure_field import AzureDIField, AzureDIFieldType
from .table_description import TableDescription

__all__ = ["EventFactory"]


class EventFactory:
    CHECKMARK_TYPE = "checkmark"
    DEFAULT_DATE_FORMAT = "%m/%d/%Y"

    @classmethod
    def _field_type_mapper(cls, type_: AzureDIFieldType) -> str:
        if type_ in {AzureDIFieldType.STRING, AzureDIFieldType.TABLE, AzureDIFieldType.DATE}:
            return AzureDIFieldType(type_)

        elif type_ is AzureDIFieldType.SELECTION_MARK:
            return cls.CHECKMARK_TYPE

        return AzureDIFieldType.STRING

    @classmethod
    def _field_description_mapper(
        cls,
        _type: AzureDIFieldType,
        description: Optional[TableDescription],
    ) -> FieldDescription | None:
        if _type == AzureDIFieldType.DATE:
            return {"format": cls.DEFAULT_DATE_FORMAT}

        elif description:
            return {
                "columns": [
                    {
                        "title": col.name,
                        "type": AzureDIFieldType.STRING,
                    }
                    for col in description.columns.values()
                ],
            }

    @classmethod
    def make_field_created_event(
        cls,
        document_type_id: str,
        field: AzureDIField,
    ) -> CloudExtractorFieldCreated:
        return CloudExtractorFieldCreated(
            document_type_id=document_type_id,
            code=field.code(),
            name=field.code(),
            type=cls._field_type_mapper(field.type),
            description=cls._field_description_mapper(_type=field.type, description=field.description),
        )

    @classmethod
    def make_field_updated_event(
        cls,
        document_type_id: str,
        field: AzureDIField,
    ) -> CloudExtractorFieldUpdated:
        return CloudExtractorFieldUpdated(
            document_type_id=document_type_id,
            code=field.code(),
            description=cls._field_description_mapper(_type=field.type, description=field.description),  # type: ignore
        )

    @classmethod
    def make_field_deleted_event(
        cls,
        document_type_id: str,
        code: str,
    ) -> CloudExtractorFieldDeleted:
        return CloudExtractorFieldDeleted(
            document_type_id=document_type_id,
            code=code,
        )
