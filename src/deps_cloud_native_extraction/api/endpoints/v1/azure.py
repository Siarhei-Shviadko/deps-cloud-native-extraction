from dataclasses import asdict
from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Response

from deps_cloud_native_extraction.api.endpoint_marker import MarkerRoute
from deps_cloud_native_extraction.api.endpoint_visibility import Visibility
from deps_cloud_native_extraction.application import CloudNativeExtractionApplication
from deps_cloud_native_extraction.containers import Containers

from ...serializers import (
    AzureExtractorCheckupResponse,
    AzureExtractorInfoResponse,
    CreateAzureExtractorRequest,
    CreateAzureExtractorResponse,
    UpdateAzureExtractorRequest,
    ValidateAzureCredentialsRequest,
)

__all__ = ["azure_router"]

azure_router = APIRouter(route_class=MarkerRoute, prefix="/azure", tags=["Azure"])


@azure_router.post(
    "/extractor",
    openapi_extra={"visibility": Visibility.PUBLIC},
    status_code=HTTPStatus.CREATED,
    response_model=CreateAzureExtractorResponse,
)
@inject
def create_azure_extractor(
    extractor_request: CreateAzureExtractorRequest,
    tenant_id: str = Depends(Provide[Containers.current_user_tenant]),
    application: CloudNativeExtractionApplication = Depends(Provide[Containers.applications.cloud_native_extraction]),
):
    document_type_id = application.create_azure_extractor(
        name=extractor_request.name,
        tenant_id=tenant_id,
        model_id=extractor_request.model_id,
        endpoint=extractor_request.endpoint,
        api_key=extractor_request.api_key,
        language=extractor_request.language,
        description=extractor_request.description,
    )

    return CreateAzureExtractorResponse.from_document_type_id(document_type_id)


@azure_router.get(
    "/extractor/{extractorId}",
    openapi_extra={"visibility": Visibility.PUBLIC},
    status_code=HTTPStatus.OK,
    response_model=AzureExtractorInfoResponse,
)
@inject
def get_azure_extractor(
    extractor_id: str = Path(..., alias="extractorId"),
    tenant_id: str = Depends(Provide[Containers.current_user_tenant]),
    application: CloudNativeExtractionApplication = Depends(Provide[Containers.applications.cloud_native_extraction]),
):
    return AzureExtractorInfoResponse(
        **asdict(application.get_azure_extractor_info(extractor_id=extractor_id, tenant_id=tenant_id)),
    )


@azure_router.put(
    "/extractor/{extractorId}",
    openapi_extra={"visibility": Visibility.PUBLIC},
    status_code=HTTPStatus.NO_CONTENT,
    response_model=None,
)
@inject
def update_azure_extractor(
    update_azure_extractor_data: UpdateAzureExtractorRequest,
    extractor_id: str = Path(..., alias="extractorId"),
    tenant_id: str = Depends(Provide[Containers.current_user_tenant]),
    application: CloudNativeExtractionApplication = Depends(Provide[Containers.applications.cloud_native_extraction]),
):
    application.update_azure_extractor(
        extractor_id=extractor_id,
        tenant_id=tenant_id,
        model_id=update_azure_extractor_data.model_id,
        endpoint=update_azure_extractor_data.endpoint,
        api_key=update_azure_extractor_data.api_key,
    )


@azure_router.post(
    "/validate-credentials",
    openapi_extra={"visibility": Visibility.PUBLIC},
    status_code=HTTPStatus.OK,
    response_class=Response,
)
@inject
def validate_credentials(
    credentials: ValidateAzureCredentialsRequest,
    application: CloudNativeExtractionApplication = Depends(Provide[Containers.applications.cloud_native_extraction]),
):
    application.validate_azure_credentials(
        endpoint=credentials.endpoint,
        model_id=credentials.model_id,
        api_key=credentials.api_key,
    )


@azure_router.get(
    "/extractor/{extractorId}/checkup",
    openapi_extra={"visibility": Visibility.PUBLIC},
    status_code=HTTPStatus.OK,
    response_model=AzureExtractorCheckupResponse,
)
@inject
def checkup(
    extractor_id: str = Path(..., alias="extractorId"),
    tenant_id: str = Depends(Provide[Containers.current_user_tenant]),
    application: CloudNativeExtractionApplication = Depends(Provide[Containers.applications.cloud_native_extraction]),
):
    checkup_info = application.azure_checkup(
        extractor_id=extractor_id,
        tenant_id=tenant_id,
    )
    return AzureExtractorCheckupResponse(status=checkup_info.status, description=checkup_info.description)


@azure_router.put(
    "/extractor/{extractorId}/synchronize",
    openapi_extra={"visibility": Visibility.PUBLIC},
    status_code=HTTPStatus.OK,
    response_class=Response,
)
@inject
def synchronize(
    extractor_id: str = Path(..., alias="extractorId"),
    tenant_id: str = Depends(Provide[Containers.current_user_tenant]),
    application: CloudNativeExtractionApplication = Depends(Provide[Containers.applications.cloud_native_extraction]),
):
    application.synchronize_azure_extractor(
        extractor_id=extractor_id,
        tenant_id=tenant_id,
    )
