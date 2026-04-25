from typing import Optional

from sqlalchemy import and_, delete, select
from sqlalchemy.dialects.postgresql import insert

from deps_cloud_native_extraction.domain.model import (
    AzureDIExtractor,
    AzureExtractorInfo,
)
from deps_cloud_native_extraction.domain.model.shared import IExtractorRepository
from deps_cloud_native_extraction.extras import DatabaseSession

from ...tables import azure_extractor_table
from .mappers import AzureDIExtractorMapper, AzureExtractorInfoMapper

__all__ = ["AzureExtractorRepository"]


class AzureExtractorRepository(IExtractorRepository[AzureDIExtractor, AzureExtractorInfo]):
    def __init__(self, database: DatabaseSession) -> None:
        self._db = database

    def get(self, id_: str, tenant_id: str) -> Optional[AzureDIExtractor]:
        query = select(azure_extractor_table).where(
            and_(
                azure_extractor_table.c.extractor_id == id_,
                azure_extractor_table.c.tenant_id == tenant_id,
            ),
        )

        with self._db.connection() as conn:
            result = conn.execute(query).fetchone()

        if result is None:
            return None

        return AzureDIExtractorMapper.from_row(result)

    def get_extractor_info(self, id_: str, tenant_id: str) -> Optional[AzureExtractorInfo]:
        query = select(
            azure_extractor_table.c.extractor_id,
            azure_extractor_table.c.model_id,
            azure_extractor_table.c.endpoint,
        ).where(
            and_(
                azure_extractor_table.c.extractor_id == id_,
                azure_extractor_table.c.tenant_id == tenant_id,
            ),
        )

        with self._db.connection() as conn:
            result = conn.execute(query).fetchone()

        if result is None:
            return None

        return AzureExtractorInfoMapper.from_row(result)

    def save(self, extractor: AzureDIExtractor) -> None:
        raw_extractor = AzureDIExtractorMapper.to_dict(extractor)

        insert_query = insert(azure_extractor_table).values(raw_extractor)
        update_query = insert_query.on_conflict_do_update(
            index_elements=[azure_extractor_table.c.extractor_id, azure_extractor_table.c.tenant_id],
            set_=raw_extractor,
        )

        with self._db.connection() as conn:
            conn.execute(update_query)

    def delete(self, id_: str, tenant_id: str) -> None:
        query = delete(azure_extractor_table).where(
            and_(
                azure_extractor_table.c.extractor_id == id_,
                azure_extractor_table.c.tenant_id == tenant_id,
            ),
        )

        with self._db.connection() as conn:
            conn.execute(query)
