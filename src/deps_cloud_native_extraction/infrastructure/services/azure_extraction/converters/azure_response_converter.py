import logging

from azure.ai.documentintelligence.models import (
    AnalyzedDocument,
    AnalyzeResult,
    DocumentField,
    DocumentFieldSchema,
    DocumentTypeDetails,
)
from deps_extracted_data import ExtractedData

from deps_cloud_native_extraction.domain.model import AzureDIField, FieldCode
from deps_cloud_native_extraction.infrastructure.proxies import UnifiedDataImage

from .exceptions import AzureFieldConversionError
from .types import (
    AbstractConverter,
    ArrayConverter,
    ObjectConverter,
    SelectionMarkConverter,
    StringConverter,
)

__all__ = ["AzureResponseConverter"]


class AzureResponseConverter:
    def __init__(
        self,
        azure_model_schema: dict[str, DocumentFieldSchema],
        extractor_schema: dict[FieldCode, AzureDIField],
        azure_extraction_response: AnalyzeResult,
        unified_images: list[UnifiedDataImage],
    ) -> None:
        self._fields_schema = azure_model_schema
        self._extractor_schema = extractor_schema
        self._response = azure_extraction_response
        self._unified_images = unified_images

        self._converters: list[AbstractConverter] = [
            StringConverter(azure_model_schema, azure_extraction_response, unified_images),
            SelectionMarkConverter(azure_model_schema, azure_extraction_response, unified_images),
            ArrayConverter(azure_model_schema, azure_extraction_response, unified_images),
            ObjectConverter(azure_model_schema, azure_extraction_response, unified_images),
        ]

        self._logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def handling_response(
        cls,
        azure_extractor_type_response: DocumentTypeDetails,
        extractor_schema: dict[FieldCode, AzureDIField],
        azure_extraction_response: AnalyzeResult,
        unified_images: list[UnifiedDataImage],
    ) -> "AzureResponseConverter":
        return cls(
            azure_model_schema=azure_extractor_type_response.field_schema,
            extractor_schema=extractor_schema,
            azure_extraction_response=azure_extraction_response,
            unified_images=unified_images,
        )

    def compose_extracted_data(self, edata: ExtractedData) -> ExtractedData:
        if len(self._response.documents) != 1:
            self._logger.warning(f"Expected 1 document in response, but got {len(self._response.documents)}")

        document: AnalyzedDocument = self._response.documents[0]

        for field_code, field in document.fields.items():
            edata = self._add_converted_field(edata=edata, field_code=field_code, field=field)

        return edata

    def _add_converted_field(self, edata: ExtractedData, field_code: str, field: DocumentField) -> ExtractedData:
        if field_code not in self._extractor_schema:
            self._logger.info(
                f"Field `{field_code}` is skipped because it is not present in the extractor schema",
            )

            return edata

        if (converter := self._field_converter(field)) is None:
            self._logger.warning(
                f"Field `{field_code}` with type `{field.type}` is not supported by any converter right now...",
            )
            return edata

        try:
            edata = converter.convert(
                edata=edata,
                field_code=field_code,
                field_data=field,
            )
        except AzureFieldConversionError as err:
            self._logger.error(
                f"Error occurred when trying to convert field `{field_code}` with type `{field.type}`: {err}",
            )

        return edata

    def _field_converter(self, field: DocumentField) -> AbstractConverter | None:
        return next(
            filter(
                lambda converter: converter.handles(field),
                self._converters,
            ),
            None,
        )
