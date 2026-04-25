import pytest

from deps_cloud_native_extraction.infrastructure.services.azure_extraction.converters.types import (
    StringConverter,
)


@pytest.mark.parametrize(
    "field_code,expected_bbox,expected_page",
    [
        ("page1_string_1", (0.2048, 0.0946, 0.12181, 0.02041), "1"),
        ("page3_string1", (0.21885882, 0.0945, 0.13362, 0.02051), "3"),
        ("page3_date", (0.194376, 0.31488, 0.11292, 0.01931), "3"),
    ],
)
def test_coordinates_conversion(
    corresponding_azure_extractor,
    test_azure_response,
    test_unified_images,
    field_code,
    expected_bbox,
    expected_page,
):
    converter = StringConverter(corresponding_azure_extractor.field_schema, test_azure_response, test_unified_images)

    field = test_azure_response.documents[0].fields[field_code]

    coordinates = converter.relative_coordinates_for(field)

    assert coordinates[0].source_id.value == expected_page
    assert round(coordinates[0].bboxes[0].x, 4) == round(expected_bbox[0], 4)
    assert round(coordinates[0].bboxes[0].y, 4) == round(expected_bbox[1], 4)
    assert round(coordinates[0].bboxes[0].w, 4) == round(expected_bbox[2], 4)
    assert round(coordinates[0].bboxes[0].h, 4) == round(expected_bbox[3], 4)


def test_coordinates_conversion__not_found_field(
    corresponding_azure_extractor,
    test_azure_response,
    test_unified_images,
):
    converter = StringConverter(
        corresponding_azure_extractor.field_schema,
        test_azure_response,
        test_unified_images[:1],
    )

    field = test_azure_response.documents[0].fields["page3_date"]

    with pytest.raises(RuntimeError):
        converter.relative_coordinates_for(field)
