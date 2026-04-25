from typing import Any

from deps_cloud_native_extraction.domain.model import AzureDIField, AzureDIFieldType

from .table_description import TableDescriptionMapper

__all__ = ["AzureDIFieldMapper"]


class AzureDIFieldMapper:
    @staticmethod
    def to_dict(field: AzureDIField) -> dict[str, Any]:
        return {
            "code": field.code(),
            "type": field.type.value,
            "description": None if field.description is None else TableDescriptionMapper.to_dict(field.description),
        }

    @staticmethod
    def from_dict(field_dict: dict[str, Any]) -> AzureDIField:
        return AzureDIField(
            code=field_dict["code"],
            _type=AzureDIFieldType(field_dict["type"]),
            description=(
                TableDescriptionMapper.from_dict(table_description_dict)
                if (table_description_dict := field_dict["description"])
                else None
            ),
        )
