from ...exceptions import InconsistentColumnFieldType
from ..shared import Guard, ImmutableCheck
from ..types import RawAzureColumn
from .azure_field_type import AzureDIFieldType

__all__ = ["Column", "VALID_COLUMN_FIELD_TYPES"]

VALID_COLUMN_FIELD_TYPES = (
    AzureDIFieldType.STRING,
    AzureDIFieldType.NUMBER,
    AzureDIFieldType.DATE,
    AzureDIFieldType.SELECTION_MARK,
)


class Column:
    name = Guard[str](str, ImmutableCheck())
    type = Guard[AzureDIFieldType](AzureDIFieldType, ImmutableCheck())

    def __init__(self, name: str, _type: AzureDIFieldType) -> None:
        self.name = name
        self.type = _type

        self._validate_type()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Column) and self.name == other.name and self.type == other.type

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.name = },",
                f"{self.type = }>",
            ),
        )

    def _validate_type(self) -> None:
        if self.type not in VALID_COLUMN_FIELD_TYPES:
            raise InconsistentColumnFieldType(type_=self.type.value)

    def to_dict(self) -> RawAzureColumn:
        return {"name": self.name, "type": self.type}
