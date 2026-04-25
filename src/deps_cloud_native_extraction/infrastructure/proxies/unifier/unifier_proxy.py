import logging

from ..exceptions import UnifierProxyError
from ..proxy import GenericProxy
from .element_type import UnifiedDataElement
from .unified_data_image import UnifiedDataImage

__all__ = ["UnifierProxy"]


class UnifierProxy(GenericProxy):
    exception = UnifierProxyError
    v1_url = "api/unifier/v1"

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

        self._logger = logging.getLogger(self.__class__.__name__)

    def get_original_images(
        self,
        document_id: str,
    ) -> list[UnifiedDataImage]:
        params = {"unified_data_types": [UnifiedDataElement.IMAGE]}

        response = self._session.get(
            url=f"{self.base_url}/{self.v1_url}/unified_data/{document_id}",
            params=params,
        )

        self._check_response(response)

        udata = response.json()

        return [UnifiedDataImage.from_dict(image) for image in udata["elements"] if image["originalImageId"] is None]
