from pydantic import Field

from .base import ConfiguredBaseModel

__all__ = ["BuildInfoSerializer"]


class BuildInfoSerializer(ConfiguredBaseModel):
    build_tag: str = Field(default="", alias="buildTag")
    build_date: str = Field(default="", alias="buildDate")
    commit_hash: str = Field(default="", alias="commitHash")
