from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, status

from deps_cloud_native_extraction.api.endpoint_marker import MarkerRoute
from deps_cloud_native_extraction.api.endpoint_visibility import Visibility
from deps_cloud_native_extraction.containers import Containers
from deps_cloud_native_extraction.extras import DatabaseSession

__all__ = ["healthcheck_router"]

healthcheck_router = APIRouter(route_class=MarkerRoute)


@healthcheck_router.get(
    "/healthcheck",
    tags=["Debug"],
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def service_healthcheck(datasource: DatabaseSession = Depends(Provide[Containers.datasources.postgres_session])):
    """Check connection to database."""
    try:
        datasource.healthcheck()
    except Exception:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(status_code=status.HTTP_200_OK)
