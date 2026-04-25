from typing import Optional

from deps_message_flow.events.common import DomainEvent

from ...exceptions import ChangeTypeError, FieldAlreadyExistsError, FieldNotFoundError
from ..shared import EntityId, Guard, ImmutableCheck, TenantId
from ..types import RawAzureDocumentType, RawTableDescription
from .azure_field import AzureDIField
from .azure_field_type import AzureDIFieldType
from .event_factory import EventFactory
from .table_description import TableDescription
from .table_description_column import Column

__all__ = ["AzureDIExtractor", "FieldCode"]


FieldCode = str


class AzureDIExtractor:
    id = Guard[EntityId](EntityId, ImmutableCheck())
    tenant_id = Guard[TenantId](TenantId, ImmutableCheck())
    model_id = Guard[str](str)
    endpoint = Guard[str](str)
    vault_key_id = Guard[str](str)
    schema = Guard[dict[FieldCode, AzureDIField]](dict)

    def __init__(
        self,
        _id: str,
        tenant_id: str,
        model_id: str,
        endpoint: str,
        vault_key_id: str,
        schema: dict[FieldCode, AzureDIField],
        *,
        events: Optional[list[DomainEvent]] = None,
    ) -> None:
        self.id = EntityId(_id)
        self.tenant_id = TenantId(tenant_id)
        self.model_id = model_id
        self.endpoint = self._normalize_endpoint(endpoint)
        self.vault_key_id = vault_key_id
        self.schema = schema

        self._events = events or []

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"<class '{self.__class__.__name__}':",
                f"{self.id = },",
                f"{self.tenant_id = },",
                f"{self.model_id = },",
                f"{self.endpoint = },",
                f"{self.vault_key_id = },",
                f"{self.schema = }>",
            ),
        )

    @property
    def events(self) -> list[DomainEvent]:
        return self._events

    @property
    def vault_key_name(self) -> str:
        return self._extract_key_vault_elements(1)

    @property
    def vault_key_version(self) -> str:
        return self._extract_key_vault_elements(-1)

    def track_schema_updates(self, updated_model: RawAzureDocumentType) -> None:
        field_codes_to_delete = set(self.schema).difference(updated_model["field_schema"])

        for field in updated_model["field_schema"].values():
            if field["code"] in self.schema:
                self._update_field(code=field["code"], _type=field["type"], description=field["description"])
            else:
                self._add_field(code=field["code"], _type=field["type"], description=field["description"])

        for code in field_codes_to_delete:
            self.delete_field(code)

    def delete_field(self, code: str) -> None:
        if field := self.schema.pop(code, None):
            self._events.append(
                EventFactory.make_field_deleted_event(
                    document_type_id=self.id(),
                    code=field.code(),
                ),
            )

    def update(self, model_id: str, endpoint: str, vault_key_id: str) -> None:
        self.model_id = model_id
        self.endpoint = self._normalize_endpoint(endpoint)
        self.vault_key_id = vault_key_id

    def _update_field(self, code: str, _type: AzureDIFieldType, description: Optional[RawTableDescription]) -> None:
        if (field := self.schema.get(code)) is None:
            raise FieldNotFoundError(code)

        new_description = self._create_field_description_from(description) if description else None

        if self._field_can_be_updated(field=field, _type=_type, description=new_description):
            updated_field = field.create_updated(_type, new_description)
            self.schema[updated_field.code()] = updated_field
            self._events.append(
                EventFactory.make_field_updated_event(
                    document_type_id=self.id(),
                    field=updated_field,
                ),
            )

    def _add_field(self, code: str, _type: AzureDIFieldType, description: Optional[RawTableDescription]) -> None:
        if code in self.schema:
            raise FieldAlreadyExistsError(code)

        field = AzureDIField(
            code=code,
            _type=_type,
            description=(self._create_field_description_from(description) if description else None),
        )

        self.schema[field.code()] = field

        self._events.append(
            EventFactory.make_field_created_event(
                document_type_id=self.id(),
                field=field,
            ),
        )

    def _extract_key_vault_elements(self, index: int) -> str:
        return self.vault_key_id.rsplit("/", maxsplit=2)[index]

    @staticmethod
    def _create_field_description_from(raw_description: RawTableDescription) -> TableDescription:
        return TableDescription(
            columns=(
                {column["name"]: Column(column["name"], _type=column["type"]) for column in raw_description["columns"]}
            ),
        )

    @staticmethod
    def _field_can_be_updated(
        field: AzureDIField,
        _type: AzureDIFieldType,
        description: Optional[TableDescription],
    ) -> bool:
        if _type != field.type:
            raise ChangeTypeError()
        return description != field.description

    @staticmethod
    def _normalize_endpoint(endpoint: str) -> str:
        return endpoint.rstrip("/") if endpoint else endpoint
