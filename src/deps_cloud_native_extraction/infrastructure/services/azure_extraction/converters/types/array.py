from typing import Iterable

from azure.ai.documentintelligence.models import DocumentField, DocumentFieldType

from ._abstract_table_converter import AbstractTableConverter

__all__ = ["ArrayConverter"]


class ArrayConverter(AbstractTableConverter):
    """Converts Dynamic Azure Tables into ExtractedData Tables"""

    def handles(self, field: DocumentField) -> bool:
        return field.type == DocumentFieldType.ARRAY and field.value_array is not None

    def _list_table_rows_for(self, data: DocumentField) -> Iterable[DocumentField]:
        return data.value_array
