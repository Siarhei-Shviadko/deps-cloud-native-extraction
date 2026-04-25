import enum

__all__ = ["UnifiedDataElement"]


class UnifiedDataElement(str, enum.Enum):
    IMAGE = "image"
    POSITIONAL_TEXT = "positional_text"
    TABLE = "table"
