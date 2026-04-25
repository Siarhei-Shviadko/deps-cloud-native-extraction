from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent

from ..model.types import FieldDescription, RawEventTableDescription

__all__ = ["CloudExtractorFieldCreated", "CloudExtractorFieldUpdated", "CloudExtractorFieldDeleted"]


@dataclass
class CloudExtractorFieldCreated(DomainEvent):
    document_type_id: str
    code: str
    name: str
    type: str
    description: FieldDescription | None
    required: bool = False
    order: int = 0


@dataclass
class CloudExtractorFieldUpdated(DomainEvent):
    document_type_id: str
    code: str
    description: RawEventTableDescription | None


@dataclass
class CloudExtractorFieldDeleted(DomainEvent):
    document_type_id: str
    code: str
