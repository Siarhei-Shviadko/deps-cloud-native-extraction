from typing import Any

from deps_cloud_native_extraction.domain.model import TableDescription

from .column import ColumnMapper

__all__ = ["TableDescriptionMapper"]


class TableDescriptionMapper:
    @staticmethod
    def to_dict(table_description: TableDescription) -> dict[str, Any]:
        return {
            "columns": {
                column_name: ColumnMapper.to_dict(column) for column_name, column in table_description.columns.items()
            },
        }

    @staticmethod
    def from_dict(table_description_dict: dict[str, Any]) -> TableDescription:
        return TableDescription(
            columns={
                column_name: ColumnMapper.from_dict(column)
                for column_name, column in table_description_dict["columns"].items()
            },
        )
