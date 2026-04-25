from dataclasses import dataclass
from enum import Enum

__all__ = ["ExtractorStatus", "ExtractorCheckupInfo", "ExtractorCheckupInfoFactory"]


class ExtractorStatus(str, Enum):
    SYNCHRONIZED = "Synchronized"
    UNSYNCHRONIZED = "Unsynchronized"
    API_KEY_EXPIRED = "API Key expired"
    ERROR = "Error"


@dataclass
class ExtractorCheckupInfo:
    status: ExtractorStatus
    description: str


class ExtractorCheckupInfoFactory:
    @classmethod
    def make_checkup_info(cls, difference: set[str]) -> ExtractorCheckupInfo:
        if difference:
            return ExtractorCheckupInfo(
                status=ExtractorStatus.UNSYNCHRONIZED,
                description=f"The fields schema is not synchronized. Difference: {cls._build_details_string(difference)}",
            )

        return ExtractorCheckupInfo(
            status=ExtractorStatus.SYNCHRONIZED,
            description="The fields schema is synchronized.",
        )

    @classmethod
    def make_api_key_expired_checkup_info(cls, details: tuple[str]) -> ExtractorCheckupInfo:
        return ExtractorCheckupInfo(
            status=ExtractorStatus.API_KEY_EXPIRED,
            description=f"The API Key has expired. Details: {cls._build_details_string(details)}",
        )

    @classmethod
    def make_error_checup_info(cls, details: tuple[str]) -> ExtractorCheckupInfo:
        return ExtractorCheckupInfo(
            status=ExtractorStatus.ERROR,
            description=f"An error occurred. Details: {cls._build_details_string(details)}",
        )

    @staticmethod
    def _build_details_string(details: tuple[str] | set[str]) -> str:
        return ", ".join(details)
