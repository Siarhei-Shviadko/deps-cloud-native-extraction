from deps_cloud_native_extraction.domain.model import AzureDIExtractor
from deps_cloud_native_extraction.infrastructure.repositories import (
    AzureExtractorRepository,
)


def compare_azure_extractors(extractor1: AzureDIExtractor, extractor2: AzureDIExtractor) -> None:
    assert extractor1 == extractor2
    assert extractor1.tenant_id == extractor2.tenant_id
    assert extractor1.model_id == extractor2.model_id
    assert extractor1.endpoint == extractor2.endpoint
    assert extractor1.vault_key_id == extractor2.vault_key_id
    assert extractor1.schema == extractor2.schema


def test_save_and_get__saved_and_found(
    azure_extractor_repository: AzureExtractorRepository,
    azure_extractor: AzureDIExtractor,
):
    azure_extractor_repository.save(azure_extractor)

    saved_azure_extractor = azure_extractor_repository.get(
        id_=azure_extractor.id(),
        tenant_id=azure_extractor.tenant_id(),
    )

    assert saved_azure_extractor is not None
    compare_azure_extractors(extractor1=azure_extractor, extractor2=saved_azure_extractor)


def test_get__does_not_exist__none(
    azure_extractor_repository: AzureExtractorRepository,
    azure_extractor: AzureDIExtractor,
):
    assert azure_extractor_repository.get(id_=azure_extractor.id(), tenant_id=azure_extractor.tenant_id()) is None


def test_get_info__found(
    azure_extractor_repository: AzureExtractorRepository,
    azure_extractor: AzureDIExtractor,
):
    azure_extractor_repository.save(azure_extractor)

    saved_azure_extractor_info = azure_extractor_repository.get_extractor_info(
        id_=azure_extractor.id(),
        tenant_id=azure_extractor.tenant_id(),
    )

    assert saved_azure_extractor_info is not None
    assert saved_azure_extractor_info.id == azure_extractor.id()
    assert saved_azure_extractor_info.model_id == azure_extractor.model_id
    assert saved_azure_extractor_info.endpoint == azure_extractor.endpoint


def test_get_info__does_not_exist__none(
    azure_extractor_repository: AzureExtractorRepository,
    azure_extractor: AzureDIExtractor,
):
    assert (
        azure_extractor_repository.get_extractor_info(
            id_=azure_extractor.id(),
            tenant_id=azure_extractor.tenant_id(),
        )
        is None
    )


def test_delete__deleted(
    azure_extractor_repository: AzureExtractorRepository,
    azure_extractor: AzureDIExtractor,
):
    azure_extractor_repository.save(azure_extractor)

    assert azure_extractor_repository.get(id_=azure_extractor.id(), tenant_id=azure_extractor.tenant_id()) is not None

    azure_extractor_repository.delete(id_=azure_extractor.id(), tenant_id=azure_extractor.tenant_id())

    assert azure_extractor_repository.get(id_=azure_extractor.id(), tenant_id=azure_extractor.tenant_id()) is None


def test_delete__does_not_exist__no_error(
    azure_extractor_repository: AzureExtractorRepository,
    azure_extractor: AzureDIExtractor,
):
    azure_extractor_repository.delete(id_=azure_extractor.id(), tenant_id=azure_extractor.tenant_id())
