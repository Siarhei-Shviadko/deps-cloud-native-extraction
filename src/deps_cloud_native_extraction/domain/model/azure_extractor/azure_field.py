from typing import Optional

from ...exceptions import InconsistentFieldTypeDescription
from ..shared import EntityId, Guard, ImmutableCheck
from .azure_field_type import AzureDIFieldType
from .table_description import TableDescription

__all__ = ["AzureDIField"]


class AzureDIField:
    code = Guard[EntityId](EntityId, ImmutableCheck())
    type = Guard[AzureDIFieldType](AzureDIFieldType, ImmutableCheck())
    description = Guard[TableDescription](TableDescription, ImmutableCheck())

    def __init__(
        self,
        code: str,
        _type: AzureDIFieldType,
        description: Optional[TableDescription] = None,
    ) -> None:
        self.code = EntityId(code)
        self.type = _type

        if description is not None:
            self.description = description

        self._validate_field_description()

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, AzureDIField)
            and self.code == other.code
            and self.type == other.type
            and self.description == other.description
        )

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.code = },",
                f"{self.type = },",
                f"{self.description = }>",
            ),
        )

    def create_updated(self, _type: AzureDIFieldType, description: Optional[TableDescription]) -> "AzureDIField":
        return AzureDIField(code=self.code(), _type=_type, description=description)

    def _validate_field_description(self) -> None:
        if (self.type == AzureDIFieldType.TABLE and self.description is None) or (
            self.type != AzureDIFieldType.TABLE and self.description
        ):
            raise InconsistentFieldTypeDescription(type_=self.type)
