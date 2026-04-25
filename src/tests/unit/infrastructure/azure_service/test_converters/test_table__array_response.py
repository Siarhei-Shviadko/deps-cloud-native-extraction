from azure.ai.documentintelligence.models import AnalyzeResult, DocumentTypeDetails
from deps_extracted_data import ExtractedDataFactory

from deps_cloud_native_extraction.domain.model import AzureDIExtractor
from deps_cloud_native_extraction.infrastructure.proxies import UnifiedDataImage
from deps_cloud_native_extraction.infrastructure.services.azure_extraction.converters import (
    AzureResponseConverter,
)

from .utils import assert_source_coordinates_correct

_expected_table_cells = [
    {
        "value": "Column1",
        "confidence": 0.983,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.12634117647058823, 0.7178818181818182, 0.08551764705882353, 0.01497272727272736]],
            }
        ],
    },
    {
        "value": "Column2",
        "confidence": 0.982,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.27135294117647063, 0.7174454545454545, 0.08595294117647057, 0.015200000000000102]],
            }
        ],
    },
    {
        "value": "Column3",
        "confidence": 0.982,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.4157294117647059, 0.7174454545454545, 0.0842705882352941, 0.015627272727272823]],
            }
        ],
    },
    {
        "value": "Column4",
        "confidence": 0.982,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.5606705882352941, 0.7178818181818182, 0.08258823529411763, 0.014754545454545354]],
            }
        ],
    },
    {
        "value": "Row1",
        "confidence": 0.984,
        "source_bbox_coordinates": [
            {"source_id": "1", "bboxes": [[0.1264, 0.7400181818181818, 0.053941176470588215, 0.013890909090909065]]}
        ],
    },
    {
        "value": "Value1",
        "confidence": 0.981,
        "source_bbox_coordinates": [
            {"source_id": "1", "bboxes": [[0.27127058823529415, 0.7398, 0.06251764705882351, 0.014972727272727249]]}
        ],
    },
    {
        "value": "Value2",
        "confidence": 0.97,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.4162941176470588, 0.7395818181818182, 0.06348235294117649, 0.015190909090909033]],
            }
        ],
    },
    {
        "value": "Value3",
        "confidence": 0.981,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.5606705882352941, 0.7395818181818182, 0.06245882352941168, 0.015409090909090817]],
            }
        ],
    },
    {
        "value": "Row2",
        "confidence": 0.987,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.12584705882352942, 0.7621545454545454, 0.05402352941176469, 0.01453636363636368]],
            }
        ],
    },
    {
        "value": "Value4",
        "confidence": 0.981,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.4157294117647059, 0.7621545454545454, 0.06131764705882348, 0.01453636363636368]],
            }
        ],
    },
    {
        "value": "Value5",
        "confidence": 0.98,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.5595529411764706, 0.7617181818181818, 0.06348235294117643, 0.015190909090909033]],
            }
        ],
    },
    {
        "value": "Row3",
        "confidence": 0.98,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.12574117647058825, 0.7847181818181818, 0.05245882352941175, 0.014981818181818207]],
            }
        ],
    },
    {
        "value": "Value6",
        "confidence": 0.98,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.2712588235294118, 0.7842909090909091, 0.0619764705882353, 0.01582727272727258]],
            }
        ],
    },
    {
        "value": "Value7",
        "confidence": 0.978,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.5601176470588235, 0.7840727272727274, 0.06357647058823535, 0.015836363636363537]],
            }
        ],
    },
    {
        "value": "Row4",
        "confidence": 0.984,
        "source_bbox_coordinates": [
            {"source_id": "1", "bboxes": [[0.1264, 0.8064272727272727, 0.052247058823529396, 0.015190909090909255]]}
        ],
    },
    {
        "value": "Value8",
        "confidence": 0.982,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.2706941176470588, 0.8062090909090909, 0.06525882352941176, 0.016272727272727328]],
            }
        ],
    },
    {
        "value": "Value9",
        "confidence": 0.981,
        "source_bbox_coordinates": [
            {
                "source_id": "1",
                "bboxes": [[0.41555294117647057, 0.8064272727272727, 0.06254117647058821, 0.015618181818181975]],
            }
        ],
    },
]


def test_azure_array_edata_conversion(
    corresponding_azure_extractor: DocumentTypeDetails,
    test_azure_response__array_only: AnalyzeResult,
    test_unified_images: list[UnifiedDataImage],
    saved_azure_extractor_with_corresponding_schema: AzureDIExtractor,
):
    converter = AzureResponseConverter.handling_response(
        azure_extractor_type_response=corresponding_azure_extractor,
        extractor_schema=saved_azure_extractor_with_corresponding_schema.schema,
        azure_extraction_response=test_azure_response__array_only,
        unified_images=test_unified_images,
    )

    edata = converter.compose_extracted_data(edata=ExtractedDataFactory.make_extracted_data(document_id=1))

    assert edata.document_id == 1
    assert len(edata.table_fields) == 1

    table = edata.table_fields[0]

    assert len(table.data.columns) == 4
    assert len(table.data.rows) == 5
    assert len(table.data.cells) == 17

    for cell, expected_cell in zip(table.data.cells, _expected_table_cells):
        assert cell.value == expected_cell["value"]
        assert cell.confidence == expected_cell["confidence"]

        assert_source_coordinates_correct(cell.source_bbox_coordinates, expected_cell["source_bbox_coordinates"])  # type: ignore
