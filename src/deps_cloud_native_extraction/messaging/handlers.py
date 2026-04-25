import contextlib
import logging
import sys

from azure.core.exceptions import HttpResponseError
from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.common import (
    CommandMessageHeaders,
    make_message_for_command,
)
from deps_message_flow.commands.consumer import (
    CommandHandlerReplyBuilder,
    CommandMessage,
)
from deps_message_flow.events.mappers import JsonMapper
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)
from deps_message_flow.messaging.common import IMessage

from deps_cloud_native_extraction.application import CloudNativeExtractionApplication
from deps_cloud_native_extraction.containers import Containers
from deps_cloud_native_extraction.domain.exceptions import BusinessException
from deps_cloud_native_extraction.infrastructure.services import AzureExtractionService

from .commands import PerformCloudNativeExtraction, PerformExtractionStepReply
from .error_type import ErrorType
from .events import DocumentTypeDeleted, ExtractorFieldDeleted

__all__ = ["perform_cloud_native_extraction_handler", "document_type_deleted_handler", "extractor_field_deleted"]

logger = logging.getLogger(__name__)

REPLY_TO_MOCK = "NONE"


@inject
def document_type_deleted_handler(
    dee: DomainEventEnvelope[DocumentTypeDeleted],
    azure_service: AzureExtractionService = Provide[Containers.services.azure],
) -> None:
    with contextlib.suppress(HttpResponseError):
        azure_service.delete_extractor(tenant_id=dee.event.tenant, extractor_id=dee.event.document_type)


@inject
def perform_cloud_native_extraction_handler(
    command_message: CommandMessage[PerformCloudNativeExtraction],
    tenant_id: str = Provide[Containers.current_user_tenant],
    app: CloudNativeExtractionApplication = Provide[Containers.applications.cloud_native_extraction],
) -> list[IMessage]:
    document_id = command_message.command.document_id
    error_type, error_message, traceback = None, None, None

    try:
        app.perform_extraction(
            document_id=document_id,
            tenant_id=tenant_id,
            extractor_id=command_message.command.extractor_id,
            extractor_type=command_message.command.extractor_type,
        )
    except BusinessException as e:
        error_type, error_message, traceback = ErrorType.BUSINESS, str(e), sys.exc_info()
    except Exception as e:
        error_type, error_message, traceback = ErrorType.SYSTEM, str(e), sys.exc_info()

    if error_type is not None:
        logger.error(
            "Failed to perform extraction for document `%s`! Reason: %s",
            document_id,
            error_message,
            exc_info=traceback,
        )

    command_reply = PerformExtractionStepReply(error_type=error_type, error_message=error_message)
    message_reply = make_message_for_command(
        channel=command_message.message.headers[CommandMessageHeaders.REPLY_TO],
        payload=JsonMapper().serialize(command_reply),
        command_type=command_reply.__class__.__name__,
        reply_to=REPLY_TO_MOCK,
    )
    return [CommandHandlerReplyBuilder.with_success(message_reply)]


@inject
def extractor_field_deleted(
    dee: DomainEventEnvelope[ExtractorFieldDeleted],
    tenant_id: str = Provide[Containers.current_user_tenant],
    app: CloudNativeExtractionApplication = Provide[Containers.applications.cloud_native_extraction],
) -> None:
    app.delete_extractor_field(
        extractor_id=dee.event.document_type_code,
        tenant_id=tenant_id,
        field_code=dee.event.code,
        extractor_type=dee.event.extractor_type,
    )
