from factory import Factory, LazyFunction, fuzzy
from faker import Faker

from deps_cloud_native_extraction.domain.model import (
    AzureDIFieldType,
    Column,
    TableDescription,
)

__all__ = ["TableDescriptionFactory"]

fake = Faker()


class ColumnFactory(Factory):
    class Meta:
        model = Column

    name = fake.name()
    _type = fuzzy.FuzzyChoice(
        (
            AzureDIFieldType.STRING,
            AzureDIFieldType.SELECTION_MARK,
            AzureDIFieldType.DATE,
            AzureDIFieldType.NUMBER,
        )
    )


class TableDescriptionFactory(Factory):
    class Meta:
        model = TableDescription

    columns = LazyFunction(lambda: {fake.name(): ColumnFactory()})
