from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent

__all__ = ["DocumentTypeDeleted", "ExtractorFieldDeleted"]


@dataclass
class DocumentTypeDeleted(DomainEvent):
    document_type: str
    tenant: str


@dataclass
class ExtractorFieldDeleted(DomainEvent):
    code: str
    document_type_code: str
    extractor_type: str
