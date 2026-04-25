import pytest

from deps_cloud_native_extraction.domain.model import CloudNativeExtractorTypes


@pytest.mark.current_task
def test_delete_extractor_field__field_deleted(
    cloud_native_extraction_app,
    saved_azure_extractor,
    azure_extractor_repository,
):
    field_code_to_remove = next(k for k in saved_azure_extractor.schema.keys())
    cloud_native_extraction_app.delete_extractor_field(
        extractor_id=saved_azure_extractor.id(),
        tenant_id=saved_azure_extractor.tenant_id(),
        field_code=field_code_to_remove,
        extractor_type=CloudNativeExtractorTypes.AZURE_CLOUD_EXTRACTOR,
    )

    extractor = azure_extractor_repository.get(saved_azure_extractor.id(), saved_azure_extractor.tenant_id())
    assert field_code_to_remove not in extractor.schema.keys()


@pytest.mark.current_task
def test_delete_extractor_field__extractor_doesnt_exist__no_error(
    cloud_native_extraction_app,
    saved_azure_extractor,
    azure_extractor_repository,
):
    field_code_to_remove = next(k for k in saved_azure_extractor.schema.keys())
    cloud_native_extraction_app.delete_extractor_field(
        extractor_id="fake_id",
        tenant_id=saved_azure_extractor.tenant_id(),
        field_code=field_code_to_remove,
        extractor_type=CloudNativeExtractorTypes.AZURE_CLOUD_EXTRACTOR,
    )

    extractor = azure_extractor_repository.get(saved_azure_extractor.id(), saved_azure_extractor.tenant_id())
    assert len(extractor.schema) == len(saved_azure_extractor.schema)
    assert extractor.schema.keys() == saved_azure_extractor.schema.keys()


@pytest.mark.current_task
def test_delete_extractor_field__wrong_type__no_errors__field_not_deleted(
    cloud_native_extraction_app,
    saved_azure_extractor,
    azure_extractor_repository,
):
    field_code_to_remove = next(k for k in saved_azure_extractor.schema.keys())
    cloud_native_extraction_app.delete_extractor_field(
        extractor_id=saved_azure_extractor.id(),
        tenant_id=saved_azure_extractor.tenant_id(),
        field_code=field_code_to_remove,
        extractor_type="WrongType",
    )
    extractor = azure_extractor_repository.get(saved_azure_extractor.id(), saved_azure_extractor.tenant_id())
    assert len(extractor.schema) == len(saved_azure_extractor.schema)
    assert extractor.schema.keys() == saved_azure_extractor.schema.keys()


@pytest.mark.current_task
def test_delete_extractor_field__fake_field_code__no_errors(
    cloud_native_extraction_app,
    saved_azure_extractor,
    azure_extractor_repository,
):
    field_code_to_remove = "fake_code"
    cloud_native_extraction_app.delete_extractor_field(
        extractor_id=saved_azure_extractor.id(),
        tenant_id=saved_azure_extractor.tenant_id(),
        field_code=field_code_to_remove,
        extractor_type=CloudNativeExtractorTypes.AZURE_CLOUD_EXTRACTOR,
    )
    extractor = azure_extractor_repository.get(saved_azure_extractor.id(), saved_azure_extractor.tenant_id())
    assert len(extractor.schema) == len(saved_azure_extractor.schema)
    assert extractor.schema.keys() == saved_azure_extractor.schema.keys()
