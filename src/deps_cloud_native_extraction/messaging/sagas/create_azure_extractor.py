import logging

from deps_message_flow.sagas.orchestration_simple_dsl import SimpleSaga

from .sagas_data import CreateAzureExtractorSagaData, CreateAzureExtractorSteps

__all__ = ["CreateAzureExtractorSaga"]


class CreateAzureExtractorSaga(SimpleSaga[CreateAzureExtractorSagaData]):
    def __init__(self, steps: CreateAzureExtractorSteps) -> None:
        # fmt: off
        self._saga_definition = (
            self.step()
            .invoke_local(steps.create_extractor)
            .with_compensation(steps.delete_document_type)
            .step()
            .invoke_local(steps.create_azure_extractor)
            .with_compensation(steps.delete_extractor)
            .step()
            .invoke_local(steps.synchronize_azure_extractor)
            .build()
        )
        # fmt: on
        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: CreateAzureExtractorSagaData) -> None:
        self._logger.info("CreateAzureExtractorgSaga: %s is completed successfully", saga_id)

    def on_saga_failed(self, saga_id: str, data: CreateAzureExtractorSagaData) -> None:
        self._logger.error("CreateAzureExtractorgSaga: is failed", saga_id)

    def on_saga_rolled_back(self, saga_id: str, data: CreateAzureExtractorSagaData) -> None:
        self._logger.error("CreateAzureExtractorgSaga: %s is rolled back", saga_id)
