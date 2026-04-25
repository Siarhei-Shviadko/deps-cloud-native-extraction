from deps_cloud_native_extraction.domain.exceptions import (
    CloudNativeExtractionException,
)

__all__ = [
    "RestClientError",
    "ExtractionProxyError",
    "DocumentTypeProxyError",
    "UnifierProxyError",
    "DocumentProxyError",
]


class RestClientError(CloudNativeExtractionException):
    code = "rest_client_error"


class ExtractionProxyError(RestClientError):
    code = "extraction_proxy_error"


class DocumentTypeProxyError(RestClientError):
    code = "document_type_proxy_error"


class UnifierProxyError(RestClientError):
    code = "unifier_proxy_error"


class DocumentProxyError(RestClientError):
    code = "document_proxy_error"
