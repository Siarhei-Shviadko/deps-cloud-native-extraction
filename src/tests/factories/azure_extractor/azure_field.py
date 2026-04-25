from factory import Factory, LazyAttribute, fuzzy
from faker import Faker

from deps_cloud_native_extraction.domain.model import AzureDIField, AzureDIFieldType

from .azure_field_description import TableDescriptionFactory

__all__ = ["AzureFieldFactory"]

fake = Faker()


class AzureFieldFactory(Factory):
    class Meta:
        model = AzureDIField

    code = LazyAttribute(lambda obj: fake.uuid4())
    _type = fuzzy.FuzzyChoice(
        (
            AzureDIFieldType.STRING,
            AzureDIFieldType.SELECTION_MARK,
            AzureDIFieldType.DATE,
            AzureDIFieldType.NUMBER,
            AzureDIFieldType.TABLE,
        ),
    )
    description = LazyAttribute(lambda obj: TableDescriptionFactory() if obj._type == AzureDIFieldType.TABLE else None)
