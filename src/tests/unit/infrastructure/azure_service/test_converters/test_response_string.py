from azure.ai.documentintelligence.models import DocumentTypeDetails
from deps_extracted_data import ExtractedDataFactory

from deps_cloud_native_extraction.domain.model import AzureDIExtractor
from deps_cloud_native_extraction.infrastructure.services.azure_extraction.converters import (
    AzureResponseConverter,
)

from .utils import assert_field_correct


def test_azure_string_edata_conversion(
    corresponding_azure_extractor: DocumentTypeDetails,
    test_azure_response,
    test_unified_images,
    saved_azure_extractor_with_corresponding_schema: AzureDIExtractor,
):
    converter = AzureResponseConverter.handling_response(
        azure_extractor_type_response=corresponding_azure_extractor,
        extractor_schema=saved_azure_extractor_with_corresponding_schema.schema,
        azure_extraction_response=test_azure_response,
        unified_images=test_unified_images,
    )

    edata = converter.compose_extracted_data(edata=ExtractedDataFactory.make_extracted_data(document_id=1))

    assert edata.document_id == 1
    assert len(edata.string_fields) == 3

    _assert_string_field_correct(
        edata,
        "page1_string_1",
        "Some text1",
        0.955,
        "1",
        (0.2048, 0.0946, 0.12181, 0.02041),
    )
    _assert_string_field_correct(
        edata,
        "page3_string1",
        "Some text31",
        0.982,
        "3",
        (0.21885882, 0.0945, 0.13362, 0.02051),
    )
    _assert_string_field_correct(
        edata,
        "page3_date",
        "7/03/2024",
        0.987,
        "3",
        (0.194376, 0.31488, 0.11292, 0.01931),
    )


def _assert_string_field_correct(
    edata,
    field_code: str,
    expected_value: str,
    confidence: float,
    image_id: str,
    expected_bbox: tuple[float, float, float, float],
):
    field = next(filter(lambda f: f.field_code == field_code, edata.string_fields), None)

    assert_field_correct(
        field,
        expected_value,
        confidence,
        image_id,
        expected_bbox,
    )
