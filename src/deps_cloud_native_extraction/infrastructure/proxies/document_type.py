import logging

from .exceptions import DocumentTypeProxyError
from .proxy import GenericProxy

__all__ = ["DocumentTypeProxy"]


class DocumentTypeProxy(GenericProxy):
    exception = DocumentTypeProxyError
    v1_url = "/api/document-type/v1/types"

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

        self._logger = logging.getLogger(self.__class__.__name__)

    def delete_document_type(self, document_type_id: str) -> None:
        response = self._session.delete(url=f"{self.base_url}{self.v1_url}/{document_type_id}")

        self._check_response(response)
