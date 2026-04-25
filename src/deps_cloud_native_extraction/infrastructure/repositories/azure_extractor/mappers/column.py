from typing import Any

from deps_cloud_native_extraction.domain.model import AzureDIFieldType, Column

__all__ = ["ColumnMapper"]


class ColumnMapper:
    @staticmethod
    def to_dict(column: Column) -> dict[str, Any]:
        return {"name": column.name, "type": column.type.value}

    @staticmethod
    def from_dict(column_dict: dict[str, Any]) -> Column:
        return Column(name=column_dict["name"], _type=AzureDIFieldType(column_dict["type"]))
