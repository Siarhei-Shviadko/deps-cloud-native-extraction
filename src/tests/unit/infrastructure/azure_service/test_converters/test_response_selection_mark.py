from azure.ai.documentintelligence.models import DocumentTypeDetails
from deps_extracted_data import CheckboxValue, ExtractedData, ExtractedDataFactory

from deps_cloud_native_extraction.domain.model import AzureDIExtractor
from deps_cloud_native_extraction.infrastructure.services.azure_extraction.converters import (
    AzureResponseConverter,
)

from .utils import assert_field_correct


def test_azure_checkmarks_edata_conversion(
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
    assert len(edata.checkbox_fields) == 4

    _assert_selection_mark_field_correct(
        edata,
        "page1_checkmark_False1",
        CheckboxValue.UNCHECKED,
        0.989,
        "1",
        (0.25383529411764705, 0.38423636363636365, 0.037564705882352944, 0.03106363636363635),
    )
    _assert_selection_mark_field_correct(
        edata,
        "page1_checkmark_True4",
        CheckboxValue.CHECKED,
        0.994,
        "1",
        (0.2519058823529412, 0.48724545454545454, 0.04054117647058819, 0.03303636363636364),
    )
    _assert_selection_mark_field_correct(
        edata,
        "page2_radio_False1",
        CheckboxValue.UNCHECKED,
        0.982,
        "2",
        (0.2636588235294117, 0.5563363636363636, 0.039047058823529435, 0.025754545454545474),
    )
    _assert_selection_mark_field_correct(
        edata,
        "page2_radio_True4",
        CheckboxValue.CHECKED,
        0.972,
        "2",
        (0.26425882352941177, 0.6503181818181818, 0.03637647058823529, 0.02505454545454544),
    )


def _assert_selection_mark_field_correct(
    edata: ExtractedData,
    field_code: str,
    expected_value: CheckboxValue,
    confidence: float,
    image_id: str,
    expected_bbox: tuple[float, float, float, float],
):
    field = next(filter(lambda f: f.field_code == field_code, edata.checkbox_fields), None)

    assert_field_correct(
        field,
        expected_value,
        confidence,
        image_id,
        expected_bbox,
    )
