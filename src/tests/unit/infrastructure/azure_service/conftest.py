import json

import pytest
from azure.ai.documentintelligence.models import AnalyzeResult, DocumentTypeDetails

from deps_cloud_native_extraction.domain.model import AzureDIExtractor
from deps_cloud_native_extraction.infrastructure.proxies import UnifiedDataImage
from deps_cloud_native_extraction.infrastructure.services.azure_extraction.azure_field_schema_parser import (
    AzureFieldSchemaParser,
)


@pytest.fixture
def test_azure_response() -> AnalyzeResult:
    with open("tests/data/raw_di_response.json") as file:
        data = json.load(file)

    return AnalyzeResult(data)


@pytest.fixture
def test_azure_response__obj_only() -> AnalyzeResult:
    with open("tests/data/raw_di_response.json") as file:
        data = json.load(file)

    data["documents"][0]["fields"] = {
        field_code: field for field_code, field in data["documents"][0]["fields"].items() if field["type"] == "object"
    }

    return AnalyzeResult(data)


@pytest.fixture
def test_azure_response__array_only() -> AnalyzeResult:
    with open("tests/data/raw_di_response.json") as file:
        data = json.load(file)

    data["documents"][0]["fields"] = {
        field_code: field for field_code, field in data["documents"][0]["fields"].items() if field["type"] == "array"
    }

    return AnalyzeResult(data)


@pytest.fixture
def test_unified_images(test_azure_response) -> list[UnifiedDataImage]:
    return [
        UnifiedDataImage(
            id=str(page.page_number),
            page=page.page_number,
            blob_name="something",
            width=3,
            height=3,
        )
        for page in test_azure_response.pages
    ]


@pytest.fixture
def corresponding_azure_extractor() -> DocumentTypeDetails:
    with open("tests/data/raw_di_response_model_schema.json") as file:
        data = json.load(file)

    return DocumentTypeDetails(data)


@pytest.fixture
def saved_azure_extractor_with_corresponding_schema(
    test_saved_empty_azure_extractor: AzureDIExtractor,
) -> AzureDIExtractor:
    with open("tests/data/raw_di_response_model_schema.json") as file:
        data = json.load(file)

    model_schema = {"docTypes": {test_saved_empty_azure_extractor.model_id: data}}
    test_saved_empty_azure_extractor.track_schema_updates(
        AzureFieldSchemaParser(test_saved_empty_azure_extractor.model_id, model_schema).parse(),
    )
    return test_saved_empty_azure_extractor
