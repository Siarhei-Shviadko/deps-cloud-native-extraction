from sqlalchemy import Column, String, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from deps_cloud_native_extraction.extras import metadata

__all__ = ["azure_extractor_table"]


azure_extractor_table = Table(
    "azure_extractor",
    metadata,
    Column("extractor_id", String, primary_key=True),
    Column("tenant_id", String, nullable=False),
    Column("model_id", String, nullable=False),
    Column("endpoint", String, nullable=False),
    Column("vault_key_id", String, nullable=False),
    Column("schema", JSONB, nullable=False),
    UniqueConstraint("extractor_id", "tenant_id", name="unique_azure_extractor_id_tenant_id"),
)
