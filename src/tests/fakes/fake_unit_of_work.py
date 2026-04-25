from deps_cloud_native_extraction.infrastructure.unit_of_work import AbstractUnitOfWork

__all__ = ["FakeUnitOfWork"]


class FakeUnitOfWork(AbstractUnitOfWork):
    def __enter__(self) -> None:
        pass

    def commit(self):
        pass

    def rollback(self):
        pass
