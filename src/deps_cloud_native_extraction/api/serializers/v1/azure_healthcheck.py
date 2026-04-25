from deps_cloud_native_extraction.infrastructure.services.extractor_checkup_info import (
    ExtractorStatus,
)

from ..base import ConfiguredBaseModel

__all__ = ["AzureExtractorCheckupResponse"]


class AzureExtractorCheckupResponse(ConfiguredBaseModel):
    status: ExtractorStatus
    description: str
