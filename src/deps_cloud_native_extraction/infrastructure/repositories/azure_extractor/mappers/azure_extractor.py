from typing import Any

from sqlalchemy import Row

from deps_cloud_native_extraction.domain.model import AzureDIExtractor

from .azure_field import AzureDIFieldMapper

__all__ = ["AzureDIExtractorMapper"]


class AzureDIExtractorMapper:
    @staticmethod
    def to_dict(extractor: AzureDIExtractor) -> dict[str, Any]:
        return {
            "extractor_id": extractor.id(),
            "tenant_id": extractor.tenant_id(),
            "model_id": extractor.model_id,
            "endpoint": extractor.endpoint,
            "vault_key_id": extractor.vault_key_id,
            "schema": {field_code: AzureDIFieldMapper.to_dict(field) for field_code, field in extractor.schema.items()},
        }

    @staticmethod
    def from_row(extractor_row: Row) -> AzureDIExtractor:
        return AzureDIExtractor(
            _id=extractor_row.extractor_id,
            tenant_id=extractor_row.tenant_id,
            model_id=extractor_row.model_id,
            endpoint=extractor_row.endpoint,
            vault_key_id=extractor_row.vault_key_id,
            schema={
                field_code: AzureDIFieldMapper.from_dict(field) for field_code, field in extractor_row.schema.items()
            },
        )
