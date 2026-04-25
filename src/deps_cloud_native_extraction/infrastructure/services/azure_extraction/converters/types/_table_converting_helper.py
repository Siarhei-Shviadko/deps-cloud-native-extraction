from dataclasses import dataclass, field

from deps_extracted_data import Bbox, RawCell, SourceBboxCoordinates

__all__ = ["TableConvertingHelper"]


@dataclass
class TableConvertingHelper:
    cells: list[RawCell] = field(default_factory=list)
    top_left_coordinates: tuple[float, float] | None = None
    bottom_right_coordinates: tuple[float, float] | None = None

    _source_id: str = ""
    _row_to_coordinates: dict[int, float] = field(default_factory=dict)
    _column_to_coordinates: dict[int, float] = field(default_factory=dict)

    def track_cell(
        self,
        row_idx: int,
        column_idx: int,
        cell: RawCell,
    ) -> None:
        self.cells.append(cell)
        self._track_cell_coordinates(
            row=row_idx,
            column=column_idx,
            cell_coordinates=cell[3],
        )

    @property
    def table_coordinates(self) -> SourceBboxCoordinates | None:
        if self.top_left_coordinates is None or self.bottom_right_coordinates is None:
            return None

        return SourceBboxCoordinates(
            value=self._source_id,
            bboxes=[
                Bbox(
                    x=self.top_left_coordinates[0],
                    y=self.top_left_coordinates[1],
                    w=self.bottom_right_coordinates[0] - self.top_left_coordinates[0],
                    h=self.bottom_right_coordinates[1] - self.top_left_coordinates[1],
                ),
            ],
        )

    @property
    def rows_y_coordinates(self) -> list[float]:
        return sorted(self._row_to_coordinates.values())

    @property
    def columns_x_coordinates(self) -> list[float]:
        return sorted(self._column_to_coordinates.values())

    def _track_cell_coordinates(
        self,
        row: int,
        column: int,
        cell_coordinates: list[SourceBboxCoordinates] | None,
    ) -> None:
        if cell_coordinates is None:
            return

        # each cell is extracted from the same page, so we can use the first source_id
        self._source_id = cell_coordinates[0].source_id.value

        # we always have only one source bbox coordinates for each cell
        cell_bbox = cell_coordinates[0].bboxes[0]

        self._track_table_disposition(cell_bbox)
        self._track_rows_disposition(row_idx=row, cell_bbox=cell_bbox)
        self._track_columns_disposition(column_idx=column, cell_bbox=cell_bbox)

    def _track_table_disposition(self, cell_bbox: Bbox) -> None:
        """We need to calculate the table coordinates from cells as we don't have them in Azure response"""

        if self.top_left_coordinates is None:
            self.top_left_coordinates = (cell_bbox.x, cell_bbox.y)
        if self.bottom_right_coordinates is None:
            self.bottom_right_coordinates = (cell_bbox.x, cell_bbox.y)

        self.top_left_coordinates = (
            min(self.top_left_coordinates[0], cell_bbox.x),
            min(self.top_left_coordinates[1], cell_bbox.y),
        )
        self.bottom_right_coordinates = (
            max(self.bottom_right_coordinates[0], cell_bbox.x + cell_bbox.w),
            max(self.bottom_right_coordinates[1], cell_bbox.y + cell_bbox.h),
        )

    def _track_rows_disposition(self, row_idx: int, cell_bbox: Bbox) -> None:
        if row_idx not in self._row_to_coordinates:
            self._row_to_coordinates[row_idx] = cell_bbox.y
            return

        self._row_to_coordinates[row_idx] = min(self._row_to_coordinates[row_idx], cell_bbox.y)

    def _track_columns_disposition(self, column_idx: int, cell_bbox: Bbox) -> None:
        if column_idx not in self._column_to_coordinates:
            self._column_to_coordinates[column_idx] = cell_bbox.x
            return

        self._column_to_coordinates[column_idx] = min(self._column_to_coordinates[column_idx], cell_bbox.x)
