from typing import Any, Dict, Optional, Type

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_message_flow.sagas.orchestration import (
    SagaCommandProducer,
    SagaDataMapping,
    SagaInstanceFactory,
    SagaManagerFactory,
)
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_cloud_native_extraction.application import CloudNativeExtractionApplication
from deps_cloud_native_extraction.constants import PROJECT_NAME
from deps_cloud_native_extraction.domain.model import IExtractorRepository
from deps_cloud_native_extraction.extras import DatabaseSession
from deps_cloud_native_extraction.infrastructure.access_management import user
from deps_cloud_native_extraction.infrastructure.proxies import (
    DocumentProxy,
    DocumentTypeProxy,
    ExtractionProxy,
    UnifierProxy,
)
from deps_cloud_native_extraction.infrastructure.repositories import (
    AzureExtractorRepository,
    SagaInstanceRepository,
)
from deps_cloud_native_extraction.infrastructure.services import (
    AzureExtractionService,
    IDocumentIntelligenceExtractor,
    OriginalFileDIExtraction,
)
from deps_cloud_native_extraction.infrastructure.unit_of_work import (
    AbstractUnitOfWork,
    SqlAlchemyUnitOfWork,
)
from deps_cloud_native_extraction.messaging.dispatcher import make_message_dispatcher
from deps_cloud_native_extraction.messaging.sagas import (
    CreateAzureExtractorSaga,
    CreateAzureExtractorSteps,
    make_saga_data_mapping,
)

MessagingClient = Type[ASBClient | KafkaClient | RabbitMQClient]


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: MessagingClient,
        message_connection_string: str,
        **kwargs: Dict[str, Any],
    ) -> Optional[MessagingClient]:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: Optional[MessagingClient]) -> None:
        if resource:
            resource.close()


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=PROJECT_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.info.tag,
            "build_date": config.info.date,
            "commit_hash": config.info.hash,
        },
    )


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres_session: providers.Provider[DatabaseSession] = providers.Singleton(
        DatabaseSession,
        username=config.user,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.db,
        dialect=config.dialect,
        driver=config.driver,
        require_secure_transport=config.require_secure_transport,
        pool_size=config.pool_size,
    )


class Repositories(containers.DeclarativeContainer):
    config = providers.Configuration()
    datasources = providers.DependenciesContainer()

    saga_instance: providers.Provider[SagaInstanceRepository] = providers.Singleton(
        SagaInstanceRepository,
        database=datasources.postgres_session,
    )
    azure_extractor: providers.Singleton[IExtractorRepository] = providers.Singleton(
        AzureExtractorRepository,
        database=datasources.postgres_session,
    )


class SagaSteps(containers.DeclarativeContainer):
    services = providers.DependenciesContainer()
    proxies = providers.DependenciesContainer()

    create_azure_extractor: providers.Singleton[CreateAzureExtractorSteps] = providers.Singleton(
        CreateAzureExtractorSteps,
        extraction_proxy=proxies.extraction,
        document_type_proxy=proxies.document_type,
        azure_service=services.azure,
    )


class Sagas(containers.DeclarativeContainer):
    messaging = providers.DependenciesContainer()
    command_producer: providers.Dependency[CommandProducer] = providers.Dependency()
    repositories = providers.DependenciesContainer()
    services = providers.DependenciesContainer()
    proxies = providers.DependenciesContainer()

    saga_steps: providers.Container[SagaSteps] = providers.Container(
        SagaSteps,
        services=services,
        proxies=proxies,
    )
    saga_command_producer: providers.Singleton[SagaCommandProducer] = providers.Singleton(
        SagaCommandProducer,
        command_producer,
    )

    saga_data_mapping: providers.Singleton[SagaDataMapping] = providers.Singleton(
        make_saga_data_mapping,
    )

    saga_manager_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaManagerFactory,
        saga_instance_repository=repositories.saga_instance,
        command_producer=command_producer,
        message_consumer=messaging.consumer,
        saga_command_producer=saga_command_producer,
        saga_data_mapping=saga_data_mapping,
    )
    sagas: providers.List = providers.List(
        providers.Singleton(CreateAzureExtractorSaga, steps=saga_steps.create_azure_extractor),
    )

    saga_instance_factory: providers.Singleton[SagaInstanceFactory] = providers.Singleton(
        SagaInstanceFactory,
        saga_manager_factory,
        sagas,
    )


class Proxies(containers.DeclarativeContainer):
    config = providers.Configuration()

    extraction: providers.Singleton[ExtractionProxy] = providers.Singleton(
        ExtractionProxy,
        base_url=config.extraction_url,
    )
    document_type: providers.Singleton[DocumentTypeProxy] = providers.Singleton(
        DocumentTypeProxy,
        base_url=config.document_type_url,
    )
    unifier: providers.Singleton[UnifierProxy] = providers.Singleton(
        UnifierProxy,
        base_url=config.unifier_url,
    )
    document: providers.Singleton[DocumentProxy] = providers.Singleton(
        DocumentProxy,
        base_url=config.document_url,
    )


class Clients(containers.DeclarativeContainer):
    config = providers.Configuration()
    proxies = providers.DependenciesContainer()

    azure_client_secret_credential: providers.Singleton[ClientSecretCredential] = providers.Singleton(
        ClientSecretCredential,
        tenant_id=config.azure.tenant_id,
        client_id=config.azure.client_id,
        client_secret=config.azure.client_secret,
    )

    azure_key_vault: providers.Singleton[SecretClient] = providers.Singleton(
        SecretClient,
        vault_url=config.azure.vault_url,
        credential=azure_client_secret_credential,
    )

    document_intelligence_extractor: providers.Singleton[IDocumentIntelligenceExtractor] = providers.Singleton(
        OriginalFileDIExtraction,
        unifier_proxy=proxies.unifier,
        document_proxy=proxies.document,
    )


class Services(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()
    clients = providers.DependenciesContainer()
    domain_event_publisher: providers.Dependency[DomainEventPublisher] = providers.Dependency()
    proxies = providers.DependenciesContainer()

    azure: providers.Singleton[AzureExtractionService] = providers.Singleton(
        AzureExtractionService,
        repository=repositories.azure_extractor,
        azure_key_vault_client=clients.azure_key_vault,
        domain_event_publisher=domain_event_publisher,
        extraction_proxy=proxies.extraction,
        document_intelligence_extractor=clients.document_intelligence_extractor,
    )


class Applications(containers.DeclarativeContainer):
    sagas = providers.DependenciesContainer()
    services = providers.DependenciesContainer()
    repositories = providers.DependenciesContainer()

    cloud_native_extraction: providers.Singleton[CloudNativeExtractionApplication] = providers.Singleton(
        CloudNativeExtractionApplication,
        azure_service=services.azure,
        azure_repository=repositories.azure_extractor,
        sagas=sagas.sagas,
        saga_instance_factory=sagas.saga_instance_factory,
    )


class Containers(containers.DeclarativeContainer):
    config = providers.Configuration()
    current_user_tenant = providers.Callable(lambda: user.get()["organisation"])
    messaging_driver_settings = providers.Dependency(instance_of=object)

    datasources: providers.Container[Datasources] = providers.Container(
        Datasources,
        config=config.database,
    )

    repositories: providers.Container[Repositories] = providers.Container(
        Repositories,
        config=config,
        datasources=datasources,
    )

    core: providers.Container[Core] = providers.Container(Core, config=config)
    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )

    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
        message_brokers=message_brokers,
    )

    command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        CommandProducer,
        messaging.producer,
    )

    domain_event_publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.producer,
    )

    message_dispatcher: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_message_dispatcher,
        messaging.consumer,
        messaging.producer,
    )

    proxies: providers.Container[Proxies] = providers.Container(
        Proxies,
        config=config,
    )
    clients: providers.Container[Clients] = providers.Container(
        Clients,
        config=config,
        proxies=proxies,
    )

    services: providers.Container[Services] = providers.Container(
        Services,
        repositories=repositories,
        clients=clients,
        domain_event_publisher=domain_event_publisher,
        proxies=proxies,
    )

    sagas: providers.Container[Sagas] = providers.Container(
        Sagas,
        messaging=messaging,
        command_producer=command_producer,
        repositories=repositories,
        services=services,
        proxies=proxies,
    )

    applications: providers.Container[Applications] = providers.Container(
        Applications,
        services=services,
        repositories=repositories,
        sagas=sagas,
    )

    unit_of_work: providers.Singleton[AbstractUnitOfWork] = providers.Singleton(
        SqlAlchemyUnitOfWork,
        database_session=datasources.postgres_session,
    )
