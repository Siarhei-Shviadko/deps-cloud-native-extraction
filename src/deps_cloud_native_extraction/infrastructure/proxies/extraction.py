import logging
from typing import Optional

from deps_extracted_data import ExtractedData
from deps_extracted_data.serializers.v2 import SerializedExtractedData

from .exceptions import ExtractionProxyError
from .proxy import GenericProxy

__all__ = ["ExtractionProxy"]


class ExtractionProxy(GenericProxy):
    exception = ExtractionProxyError
    v2_url = "/api/extraction/v2"

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

        self._logger = logging.getLogger(self.__class__.__name__)

    def attach_extractor(
        self,
        name: str,
        extractor_type: str,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        data = {
            "name": name,
            "extractorType": extractor_type,
            "engine": engine,
            "language": language,
            "description": description,
        }
        response = self._session.post(url=f"{self.base_url}{self.v2_url}/document-types/attach-extractor", json=data)

        self._check_response(response)

        return response.json()["documentTypeId"]

    def save_extracted_data(self, extracted_data: ExtractedData) -> None:
        url = f"{self._base_url}{self.v2_url}/extracted-data/{extracted_data.document_id}"
        json = SerializedExtractedData.from_model(extracted_data).dict(by_alias=True)

        response = self._session.put(url, json=json)

        self._check_response(response)
