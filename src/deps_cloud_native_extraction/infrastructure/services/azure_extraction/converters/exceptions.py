from deps_cloud_native_extraction.domain.exceptions import (
    CloudNativeExtractionException,
)

__all__ = ["AzureFieldConversionError", "AzureTableFieldConversionError"]


class AzureFieldConversionError(CloudNativeExtractionException):
    code = "azure_field_conversion_error"


class AzureTableFieldConversionError(AzureFieldConversionError):
    code = "azure_table_field_conversion_error"
