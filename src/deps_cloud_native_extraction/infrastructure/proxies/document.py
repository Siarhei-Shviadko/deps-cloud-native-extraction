import logging

from .exceptions import DocumentProxyError
from .proxy import GenericProxy

__all__ = ["DocumentProxy"]


class DocumentProxy(GenericProxy):
    exception = DocumentProxyError
    v1_url = "api/document/v1"

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

        self._logger = logging.getLogger(self.__class__.__name__)

    def get_original_file(self, document_id: str) -> bytes:
        response = self._session.get(url=f"{self._base_url}/{self.v1_url}/documents/{document_id}/files")

        self._check_response(response)

        return response.content
