from dataclasses import dataclass

from deps_message_flow.commands.common import Command

from deps_cloud_native_extraction.domain.model import CloudNativeExtractorTypes

__all__ = ["PerformCloudNativeExtraction", "PerformExtractionStepReply"]


@dataclass
class PerformCloudNativeExtraction(Command):
    extractor_type: CloudNativeExtractorTypes
    extractor_id: str
    document_id: str


@dataclass
class PerformExtractionStepReply(Command):
    error_type: str | None
    error_message: str | None
