from dataclasses import dataclass

__all__ = ["AzureExtractorInfo"]


@dataclass
class AzureExtractorInfo:
    id: str
    model_id: str
    endpoint: str
