__all__ = ["CloudNativeExtractionException", "NotFoundError", "IllegalArgument", "BusinessException"]


class CloudNativeExtractionException(Exception):
    code = "cloud_native_extraction_exception"


class BusinessException(CloudNativeExtractionException):
    code = "business_exception"


class NotFoundError(CloudNativeExtractionException):
    code = "not_found_error"


class IllegalArgument(CloudNativeExtractionException):
    code = "illegal_argument"
