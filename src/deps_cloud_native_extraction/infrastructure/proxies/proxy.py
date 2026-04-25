from requests import Response

from deps_cloud_native_extraction.extras import AbstractRESTClient, DEPSTokenAuth
from deps_cloud_native_extraction.infrastructure.access_management import user

from .exceptions import RestClientError

__all__ = ["GenericProxy"]


class GenericProxy(AbstractRESTClient):
    exception = RestClientError

    def _set_authentication(self) -> None:
        self._session.auth = DEPSTokenAuth(user)

    def _check_response(self, response: Response) -> None:
        if not response.ok:
            self._logger.error(
                "Response to %s failed with error %s",
                response.url,
                response.content,
            )
            raise self.exception(response.content)
