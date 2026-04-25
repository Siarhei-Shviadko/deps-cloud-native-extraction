from enum import Enum

__all__ = ["AzureDIFieldType"]


class AzureDIFieldType(str, Enum):
    STRING = "string"
    SELECTION_MARK = "selection_mark"
    DATE = "date"
    NUMBER = "number"
    TABLE = "table"
