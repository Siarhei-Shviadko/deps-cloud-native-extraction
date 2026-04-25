from .azure_extractor import AzureDIExtractor

__all__ = ["AzureDIExtractorFactory"]


class AzureDIExtractorFactory:
    @staticmethod
    def create_empty_extractor(
        _id: str,
        tenant_id: str,
        model_id: str,
        endpoint: str,
        vault_key_id: str,
    ) -> AzureDIExtractor:
        return AzureDIExtractor(
            _id=_id,
            tenant_id=tenant_id,
            model_id=model_id,
            endpoint=endpoint,
            vault_key_id=vault_key_id,
            schema={},
        )
