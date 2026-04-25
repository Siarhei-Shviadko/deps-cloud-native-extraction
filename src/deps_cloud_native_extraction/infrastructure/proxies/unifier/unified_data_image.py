from dataclasses import dataclass
from typing import Any, Optional

__all__ = ["UnifiedDataImage"]


@dataclass
class UnifiedDataImage:
    id: str
    page: int
    blob_name: str
    width: int
    height: int

    @classmethod
    def from_dict(cls, image: dict[str, Any]) -> "UnifiedDataImage":
        return cls(
            id=image["id"],
            page=image["page"],
            blob_name=image["blobName"],
            width=image["width"],
            height=image["height"],
        )
