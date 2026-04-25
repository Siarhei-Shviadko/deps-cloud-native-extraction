from ..shared import Guard
from .table_description_column import Column

__all__ = ["TableDescription"]


ColName = str


class TableDescription:
    columns = Guard[dict[ColName, Column]](dict)

    def __init__(self, columns: dict[ColName, Column]) -> None:
        self.columns = columns

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TableDescription) and self.columns == other.columns

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.columns = }>",
            ),
        )

    def create_updated(self, columns: list[Column]) -> "TableDescription":
        return TableDescription(columns={col.name: col for col in columns})
