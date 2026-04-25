from typing import TypedDict, Union

__all__ = ["RawEventTableDescription", "RawEventColumnDescription", "RawEventDateDescription", "FieldDescription"]


class RawEventDateDescription(TypedDict):
    format: str


class RawEventColumnDescription(TypedDict):
    title: str
    type: str


class RawEventTableDescription(TypedDict):
    columns: list[RawEventColumnDescription]


FieldDescription = Union[RawEventTableDescription, RawEventDateDescription]
