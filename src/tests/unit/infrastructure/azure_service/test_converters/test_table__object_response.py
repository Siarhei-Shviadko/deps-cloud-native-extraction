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
        "value": "Row21",
        "confidence": 0.99,
        "source_bbox_coordinates": [
            {"source_id": "2", "bboxes": [[0.12688235294117647, 0.7398, 0.06421176470588236, 0.014972727272727249]]}
        ],
    },
    {
        "value": "Value21",
        "confidence": 0.99,
        "source_bbox_coordinates": [
            {
                "source_id": "2",
                "bboxes": [[0.2707882352941176, 0.7400181818181818, 0.07528235294117652, 0.014318181818181897]],
            }
        ],
    },
    {
        "value": "Value22",
        "confidence": 0.986,
        "source_bbox_coordinates": [
            {
                "source_id": "2",
                "bboxes": [[0.4162941176470588, 0.7400181818181818, 0.07358823529411762, 0.014754545454545465]],
            }
        ],
    },
    {
        "value": "Value23",
        "confidence": 0.99,
        "source_bbox_coordinates": [
            {
                "source_id": "2",
                "bboxes": [[0.5601176470588235, 0.7400181818181818, 0.07415294117647064, 0.014754545454545465]],
            }
        ],
    },
    {
        "value": "Row22",
        "confidence": 0.99,
        "source_bbox_coordinates": [
            {"source_id": "2", "bboxes": [[0.1264, 0.7617181818181818, 0.06629411764705881, 0.015627272727272712]]}
        ],
    },
    {
        "value": "Value24",
        "confidence": 0.989,
        "source_bbox_coordinates": [
            {"source_id": "2", "bboxes": [[0.4157294117647059, 0.7617181818181818, 0.0736, 0.015190909090909033]]}
        ],
    },
    {
        "value": "Value25",
        "confidence": 0.986,
        "source_bbox_coordinates": [
            {"source_id": "2", "bboxes": [[0.5594, 0.7612818181818182, 0.0744588235294118, 0.01606363636363639]]}
        ],
    },
]


def test_azure_object_edata_conversion(
    corresponding_azure_extractor: DocumentTypeDetails,
    test_azure_response__obj_only: AnalyzeResult,
    test_unified_images: list[UnifiedDataImage],
    saved_azure_extractor_with_corresponding_schema: AzureDIExtractor,
):
    converter = AzureResponseConverter.handling_response(
        azure_extractor_type_response=corresponding_azure_extractor,
        extractor_schema=saved_azure_extractor_with_corresponding_schema.schema,
        azure_extraction_response=test_azure_response__obj_only,
        unified_images=test_unified_images,
    )

    edata = converter.compose_extracted_data(edata=ExtractedDataFactory.make_extracted_data(document_id=1))

    assert edata.document_id == 1
    assert len(edata.table_fields) == 1

    table = edata.table_fields[0]

    assert len(table.data.columns) == 4
    assert len(table.data.rows) == 2
    assert len(table.data.cells) == 7

    for cell, expected_cell in zip(table.data.cells, _expected_table_cells):
        assert cell.value == expected_cell["value"]
        assert cell.confidence == expected_cell["confidence"]

        assert_source_coordinates_correct(cell.source_bbox_coordinates, expected_cell["source_bbox_coordinates"])  # type: ignore
