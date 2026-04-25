import logging

from deps_message_flow.commands.consumer import (
    CommandDispatcher,
    CommandHandlersBuilder,
)
from deps_message_flow.events.subscriber import (
    DomainEventDispatcher,
    DomainEventHandlersBuilder,
)
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer

from deps_cloud_native_extraction.constants import (
    COMMANDS_CHANNEL,
    COMMANDS_QUEUE,
    DOCUMENT_TYPE_EXCHANGER,
    DOCUMENTS_EXCHANGER,
    EVENTS_QUEUE,
    EXTRACTOR_EXCHANGER,
)

from .commands import PerformCloudNativeExtraction
from .events import DocumentTypeDeleted, ExtractorFieldDeleted

_logger = logging.getLogger(__name__)


def make_message_dispatcher(subscriber: IMessageConsumer, producer: IMessageProducer) -> IMessageConsumer:
    from deps_cloud_native_extraction.messaging.handlers import (  # noqa: WPS433
        document_type_deleted_handler,
        extractor_field_deleted,
        perform_cloud_native_extraction_handler,
    )

    events_handlers = (
        DomainEventHandlersBuilder.for_aggregate_type(DOCUMENTS_EXCHANGER)
        .and_for_aggregate_type(DOCUMENT_TYPE_EXCHANGER)
        .on_event(DocumentTypeDeleted, document_type_deleted_handler)
        .and_for_aggregate_type(EXTRACTOR_EXCHANGER)
        .on_event(ExtractorFieldDeleted, extractor_field_deleted)
        .for_queue(EVENTS_QUEUE)
        .build()
    )

    commands_handlers = (
        CommandHandlersBuilder.from_channel(COMMANDS_CHANNEL)
        .on_message(PerformCloudNativeExtraction, perform_cloud_native_extraction_handler)
        .for_queue(COMMANDS_QUEUE)
        .build()
    )

    ded = DomainEventDispatcher(events_handlers, subscriber)
    ded.initialize()

    cd = CommandDispatcher(commands_handlers, subscriber, producer)
    cd.initialize()

    _logger.info("Start consuming....")

    return subscriber
