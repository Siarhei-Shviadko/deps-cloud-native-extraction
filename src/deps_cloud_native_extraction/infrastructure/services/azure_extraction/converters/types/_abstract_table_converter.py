import logging
from abc import ABC, abstractmethod
from typing import Iterable

from azure.ai.documentintelligence.models import DocumentField
from deps_extracted_data import ExtractedData, TableCellCoordinates

from ..exceptions import AzureTableFieldConversionError
from ._table_converting_helper import TableConvertingHelper
from .abstract import AbstractConverter

__all__ = ["AbstractTableConverter"]

_logger = logging.getLogger(__name__)


class AbstractTableConverter(AbstractConverter, ABC):
    def convert(
        self,
        edata: ExtractedData,
        field_code: str,
        field_data: DocumentField,
    ) -> ExtractedData:
        try:
            parsed_table_content: TableConvertingHelper = self._parse_table_data(field_code, field_data)
        except AttributeError as err:
            raise AzureTableFieldConversionError(
                f"Error occurred when parsing table data for field `{field_code}`: {err}",
            )

        table = self.efield_factory.create_table(
            field_code=field_code,
            columns=parsed_table_content.columns_x_coordinates,
            rows=parsed_table_content.rows_y_coordinates,
            cells=parsed_table_content.cells,
            coordinates=parsed_table_content.table_coordinates,
        )

        edata.add_table(table=table)

        return edata

    def _parse_table_data(self, code: str, data: DocumentField) -> TableConvertingHelper:
        table = TableConvertingHelper()
        indexed_column_names = {
            column_name: idx for idx, column_name in enumerate(self._schema[code].items_schema.properties.keys())
        }

        rows_array: Iterable[DocumentField] = self._list_table_rows_for(data)

        for row_idx, row in enumerate(rows_array):
            for column_name, cell in row.value_object.items():
                self._track_cell(
                    row_idx=row_idx,
                    column_name=column_name,
                    cell=cell,
                    table=table,
                    indexed_column_names=indexed_column_names,
                )

        return table

    def _track_cell(
        self,
        row_idx: int,
        column_name: str,
        cell: DocumentField,
        table: TableConvertingHelper,
        indexed_column_names: dict[str, int],
    ) -> None:
        if column_name not in indexed_column_names:
            _logger.warning(
                "DI Extracted table column `%s` which doesn't present in Extractor schema: `%s`!",
                column_name,
                str(indexed_column_names),
            )
            return

        if (cell_coordinates := self.relative_coordinates_for(cell)) is None:
            return

        table.track_cell(
            row_idx=row_idx,
            column_idx=indexed_column_names[column_name],
            cell=(
                cell.content if cell.content is not None else "",
                cell.confidence if cell.confidence is not None else -1.0,
                TableCellCoordinates(
                    row=row_idx,
                    column=indexed_column_names[column_name],
                    row_span=1,  # Document Intelligence can't detect merged cells during Extraction
                    column_span=1,
                ),
                cell_coordinates,
                None,
            ),
        )

    @abstractmethod
    def _list_table_rows_for(self, data: DocumentField) -> Iterable[DocumentField]:
        pass
