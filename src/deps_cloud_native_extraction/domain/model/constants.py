from enum import Enum

__all__ = ["CloudNativeExtractorTypes"]


class CloudNativeExtractorTypes(str, Enum):
    AZURE_CLOUD_EXTRACTOR = "azure_cloud_extractor"
