from typing import Any

from deps_asb import ASBSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from deps_cloud_native_extraction.extras import DatabaseSettings, ServiceInfoSettings


class AzureSettings(BaseSettings):
    vault_url: str
    client_id: str
    tenant_id: str
    client_secret: str

    model_config = SettingsConfigDict(
        use_enum_values=True,
        env_prefix="AZURE_",
    )


class Settings(BaseSettings):
    env: str = "development"
    version: str = "1.0"

    logger_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    info: ServiceInfoSettings = Field(default_factory=ServiceInfoSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    azure: AzureSettings = Field(default_factory=AzureSettings)

    messaging_driver: MessagingDriverEnum = Field(MessagingDriverEnum.RABBITMQ, validation_alias="MESSAGING_DRIVER")
    messaging_driver_settings: Any = Field(None, validation_alias="MESSAGING_DRIVER_SETTINGS")
    message_broker_connection_string: str

    documentation_enabled: bool = True
    instrumentation_enabled: bool = False

    extraction_url: str
    document_type_url: str
    unifier_url: str
    document_url: str

    model_config = SettingsConfigDict(use_enum_values=True)

    @field_validator("messaging_driver_settings", mode="before")
    @classmethod
    def validate_messaging_driver_settings(cls, _: Any, info) -> Any:
        messaging_driver = info.data.get("messaging_driver")

        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().model_dump()

        raise ValueError(f"Driver {driver} is not implemented")
