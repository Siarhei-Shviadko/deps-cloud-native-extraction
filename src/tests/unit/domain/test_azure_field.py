import pytest

from deps_cloud_native_extraction.domain.exceptions import (
    InconsistentColumnFieldType,
    InconsistentFieldTypeDescription,
)
from deps_cloud_native_extraction.domain.model import (
    AzureDIField,
    AzureDIFieldType,
    Column,
    TableDescription,
)
from tests.factories.azure_extractor.azure_field_description import (
    TableDescriptionFactory,
)


@pytest.mark.parametrize(
    "azure_field_type,azure_field_description",
    (
        (AzureDIFieldType.STRING, TableDescriptionFactory()),
        (AzureDIFieldType.SELECTION_MARK, TableDescriptionFactory()),
        (AzureDIFieldType.DATE, TableDescriptionFactory()),
        (AzureDIFieldType.NUMBER, TableDescriptionFactory()),
        (AzureDIFieldType.TABLE, None),
    ),
)
def test_azure_field_type_inconsistent_with_description__raised(
    test_code: str,
    azure_field_type: AzureDIFieldType,
    azure_field_description: TableDescription | None,
):
    with pytest.raises(InconsistentFieldTypeDescription):
        AzureDIField(
            code=test_code,
            _type=azure_field_type,
            description=azure_field_description,
        )


@pytest.mark.parametrize(
    "azure_field_type,azure_field_description",
    ((AzureDIFieldType.TABLE, TableDescriptionFactory()),),
)
def test_azure_field_type_consistent_with_description__success(
    test_code: str,
    azure_field_type: AzureDIFieldType,
    azure_field_description: TableDescription | None,
):
    azure_field = AzureDIField(
        code=test_code,
        _type=azure_field_type,
        description=azure_field_description,
    )
    assert azure_field.type == azure_field_type
    assert azure_field.description == azure_field_description
    assert azure_field.code() == test_code


@pytest.mark.parametrize(
    "azure_column_type",
    (
        AzureDIFieldType.STRING,
        AzureDIFieldType.SELECTION_MARK,
        AzureDIFieldType.DATE,
        AzureDIFieldType.NUMBER,
    ),
)
def test_azure_column_type_inconsistent__success(
    test_column_name: str,
    azure_column_type: AzureDIFieldType,
):
    table_column = Column(name=test_column_name, _type=azure_column_type)

    assert table_column.type == azure_column_type


@pytest.mark.parametrize(
    "azure_column_type",
    (AzureDIFieldType.TABLE,),
)
def test_azure_column_type_inconsistent__raised(
    test_column_name: str,
    azure_column_type: AzureDIFieldType,
):
    with pytest.raises(InconsistentColumnFieldType):
        Column(name=test_column_name, _type=azure_column_type)
