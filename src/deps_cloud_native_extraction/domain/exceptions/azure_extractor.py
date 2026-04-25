from .base import BusinessException, CloudNativeExtractionException, NotFoundError

__all__ = [
    "InconsistentFieldTypeDescription",
    "InconsistentColumnFieldType",
    "AzureExtractorError",
    "FieldAlreadyExistsError",
    "FieldNotFoundError",
    "ChangeTypeError",
    "AzureExtractorNotFoundError",
    "AzureExtractorInvalidCredentialsError",
    "AzureExtractorHttpClientError",
]


class InconsistentFieldTypeDescription(BusinessException):
    code = "field_type_description_inconsistent"

    def __init__(self, type_: str) -> None:
        super().__init__(f"Field has `{type_}` type that not consistent with description")


class InconsistentColumnFieldType(BusinessException):
    code = "column_type_inconsistent"

    def __init__(self, type_: str) -> None:
        super().__init__(f"Column can't have type `{type_}`")


class AzureExtractorError(CloudNativeExtractionException):
    code = "azure_extractor_error"


class FieldAlreadyExistsError(BusinessException):
    def __init__(self, code: str) -> None:
        super().__init__(f"Field with code {code} already exists.")


class FieldNotFoundError(BusinessException):
    def __init__(self, code: str) -> None:
        super().__init__(f"Field with code {code} doesn't exist.")


class ChangeTypeError(BusinessException):
    code = "field_type_mustn't be changed."


class AzureExtractorNotFoundError(NotFoundError):
    code = "azure-extractor-not-found-error"


class AzureExtractorInvalidCredentialsError(AzureExtractorError):
    code = "azure_extractor_invalid_credentials"


class AzureExtractorHttpClientError(AzureExtractorError):
    code = "azure_extractor_http_client_error"
