# type: ignore
from deps_extracted_data import SourceBboxCoordinates


def assert_field_correct(
    field,
    expected_value,
    confidence,
    image_id,
    expected_bbox,
):
    assert field is not None
    assert field.data.value == expected_value
    assert field.data.confidence == confidence
    assert len(field.data.source_bbox_coordinates) == 1

    cords = field.data.source_bbox_coordinates[0]
    assert cords.source_id.value == image_id

    assert round(cords.bboxes[0].x, 4) == round(expected_bbox[0], 4)
    assert round(cords.bboxes[0].y, 4) == round(expected_bbox[1], 4)
    assert round(cords.bboxes[0].w, 4) == round(expected_bbox[2], 4)
    assert round(cords.bboxes[0].h, 4) == round(expected_bbox[3], 4)


def assert_source_coordinates_correct(
    source_coordinates: list[SourceBboxCoordinates],
    expected_raw_coordinates: list[dict[str, str | list[tuple[float, float, float, float]]]],
):
    assert len(source_coordinates) == len(expected_raw_coordinates)

    for source_cords, expected_cords in zip(source_coordinates, expected_raw_coordinates):
        assert source_cords.source_id.value == expected_cords["source_id"]
        assert len(source_cords.bboxes) == len(expected_cords["bboxes"])

        for bbox, expected_bbox in zip(source_cords.bboxes, expected_cords["bboxes"]):
            assert round(bbox.x, 4) == round(expected_bbox[0], 4)
            assert round(bbox.y, 4) == round(expected_bbox[1], 4)
            assert round(bbox.w, 4) == round(expected_bbox[2], 4)
            assert round(bbox.h, 4) == round(expected_bbox[3], 4)
