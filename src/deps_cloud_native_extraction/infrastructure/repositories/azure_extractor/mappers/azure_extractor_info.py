from typing import Any

from sqlalchemy import Row

from deps_cloud_native_extraction.domain.model import AzureExtractorInfo

__all__ = ["AzureExtractorInfoMapper"]


class AzureExtractorInfoMapper:
    @staticmethod
    def from_row(extractor_info_row: Row) -> AzureExtractorInfo:
        return AzureExtractorInfo(
            id=extractor_info_row.extractor_id,
            model_id=extractor_info_row.model_id,
            endpoint=extractor_info_row.endpoint,
        )
