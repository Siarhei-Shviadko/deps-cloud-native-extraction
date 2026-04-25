from deps_extracted_data import Bbox, SourceBboxCoordinates, TableCellCoordinates

from deps_cloud_native_extraction.infrastructure.services.azure_extraction.converters.types._table_converting_helper import (
    TableConvertingHelper,
)


def test_track_cell():
    helper = TableConvertingHelper()
    cell = (
        "cell_value",
        0.9,
        TableCellCoordinates(0, 0, 1, 1),
        [SourceBboxCoordinates("1", [Bbox(0.1, 0.2, 0.3, 0.4)])],
        None,
    )
    helper.track_cell(0, 0, cell)

    assert len(helper.cells) == 1
    assert helper.cells[0] == cell
    assert helper._source_id == "1"
    assert helper.top_left_coordinates == (0.1, 0.2)
    assert (round(helper.bottom_right_coordinates[0], 1), round(helper.bottom_right_coordinates[1], 1)) == (0.4, 0.6)


def test_rows_y_coordinates():
    helper = TableConvertingHelper()
    helper._row_to_coordinates = {0: 0.2, 1: 0.1}
    assert helper.rows_y_coordinates == [0.1, 0.2]


def test_columns_x_coordinates():
    helper = TableConvertingHelper()
    helper._column_to_coordinates = {0: 0.3, 1: 0.4}
    assert helper.columns_x_coordinates == [0.3, 0.4]


def test_continuous_add_cells():
    helper = TableConvertingHelper()
    _tc = (TableCellCoordinates(0, 0, 1, 1),)
    cells = [
        ("cell1", 0.9, _tc, [SourceBboxCoordinates("1", [Bbox(0.1, 0.2, 0.3, 0.1)])], None),
        ("cell2", 0.9, _tc, [SourceBboxCoordinates("1", [Bbox(0.2, 0.3, 0.4, 0.2)])], None),
        ("cell3", 0.9, _tc, [SourceBboxCoordinates("1", [Bbox(0.3, 0.4, 0.5, 0.2)])], None),
        ("cell4", 0.9, _tc, [SourceBboxCoordinates("1", [Bbox(0.4, 0.5, 0.1, 0.2)])], None),
        ("cell5", 0.9, _tc, [SourceBboxCoordinates("1", [Bbox(0.5, 0.6, 0.1, 0.1)])], None),
    ]

    for i, cell in enumerate(cells):
        helper.track_cell(i, i, cell)

    assert helper.top_left_coordinates == (0.1, 0.2)
    assert helper.bottom_right_coordinates == (0.8, 0.7)
