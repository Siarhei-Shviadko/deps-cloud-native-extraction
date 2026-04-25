import logging
from typing import Any, Optional

from azure.ai.documentintelligence.models import DocumentFieldType, DocumentModelDetails

from deps_cloud_native_extraction.domain.exceptions import InconsistentColumnFieldType
from deps_cloud_native_extraction.domain.model import (
    VALID_COLUMN_FIELD_TYPES,
    AzureDIFieldType,
)
from deps_cloud_native_extraction.domain.model.types import (
    RawAzureColumn,
    RawAzureDIField,
    RawAzureDocumentType,
    RawTableDescription,
)

__all__ = ["AzureFieldSchemaParser"]


class AzureFieldSchemaParser:
    TABLE_TYPE_POINTER = DocumentFieldType.ARRAY
    TABLE_ITEM_TYPE_POINTER = DocumentFieldType.OBJECT

    def __init__(self, model_id: str, model_details: DocumentModelDetails) -> None:
        self._model_id = model_id
        self._model_details = model_details

        self._orig_type_to_azure_di_field_type_map = {
            DocumentFieldType.STRING: AzureDIFieldType.STRING,
            DocumentFieldType.DATE: AzureDIFieldType.DATE,
            DocumentFieldType.TIME: AzureDIFieldType.STRING,
            DocumentFieldType.PHONE_NUMBER: AzureDIFieldType.STRING,
            DocumentFieldType.NUMBER: AzureDIFieldType.NUMBER,
            DocumentFieldType.INTEGER: AzureDIFieldType.NUMBER,
            DocumentFieldType.SELECTION_MARK: AzureDIFieldType.SELECTION_MARK,
            DocumentFieldType.COUNTRY_REGION: AzureDIFieldType.STRING,
            DocumentFieldType.SIGNATURE: AzureDIFieldType.STRING,  # TODO: add appropriate type
            DocumentFieldType.ARRAY: AzureDIFieldType.TABLE,
            DocumentFieldType.CURRENCY: AzureDIFieldType.STRING,
            DocumentFieldType.ADDRESS: AzureDIFieldType.STRING,
            DocumentFieldType.BOOLEAN: AzureDIFieldType.STRING,  # TODO: add appropriate type
        }

        self._logger = logging.getLogger(self.__class__.__name__)

    def parse(self) -> RawAzureDocumentType:
        result = {}
        # Azure prebuilt models have a docType without the `prebuilt-` suffix
        doc_type = self._model_id.removeprefix("prebuilt-")
        try:
            field_schema = self._model_details["docTypes"][doc_type]["fieldSchema"]
            for key, data in field_schema.items():
                if raw_field := self._create_raw_field(key, data):
                    result[key] = raw_field

            return RawAzureDocumentType(field_schema=result)

        except Exception as err:
            self._logger.error(
                "Parsing field schema fails with error: %s, for model: %s with raw_data: %s",
                str(err),
                self._model_id,
                self._model_details,
                exc_info=True,
            )
            raise

    def _create_raw_field(self, key: str, data: dict[str, Any]) -> Optional[RawAzureDIField]:
        if data["type"] not in self._orig_type_to_azure_di_field_type_map:
            self._logger.warning("Original field type %s doesn't have appropriate type in service.", data["type"])

            return None

        if data["type"] == self.TABLE_TYPE_POINTER and data["items"]["type"] != self.TABLE_ITEM_TYPE_POINTER:
            self._logger.warning("Item type %s of original array field is not supported.", data["items"]["type"])

            return None

        try:
            description = (
                self._create_raw_table_description(data["items"]["properties"])
                if data["type"] == self.TABLE_TYPE_POINTER
                else None
            )
        except InconsistentColumnFieldType as error:
            self._logger.warning(
                "Original table column field type unsupported: %s",
                str(error),
            )
            return None

        return RawAzureDIField(
            code=key,
            type=self._orig_type_to_azure_di_field_type_map[data["type"]],
            description=description,
        )

    def _create_raw_table_description(self, data: dict[str, Any]) -> RawTableDescription:
        columns = []
        for name, value in data.items():
            column_type = self._orig_type_to_azure_di_field_type_map.get(value["type"], None)
            if column_type not in VALID_COLUMN_FIELD_TYPES:
                raise InconsistentColumnFieldType(type_=value["type"])

            columns.append(RawAzureColumn(name=name, type=column_type))

        return RawTableDescription(columns=columns)
