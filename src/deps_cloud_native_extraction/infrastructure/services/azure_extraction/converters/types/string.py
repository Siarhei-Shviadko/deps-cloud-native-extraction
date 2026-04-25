from azure.ai.documentintelligence.models import DocumentField, DocumentFieldType
from deps_extracted_data import ExtractedData

from .abstract import AbstractConverter

__all__ = ["StringConverter"]


class StringConverter(AbstractConverter):
    def handles(self, field: DocumentField) -> bool:
        return field.type in {
            DocumentFieldType.STRING,
            DocumentFieldType.NUMBER,
            DocumentFieldType.DATE,
            DocumentFieldType.TIME,
            DocumentFieldType.PHONE_NUMBER,
            DocumentFieldType.ADDRESS,
            DocumentFieldType.COUNTRY_REGION,
            DocumentFieldType.INTEGER,
            DocumentFieldType.CURRENCY,
        }

    def convert(
        self,
        edata: ExtractedData,
        field_code: str,
        field_data: DocumentField,
    ) -> ExtractedData:
        edata.add_string(
            string=self.efield_factory.create_string(
                field_code=field_code,
                value=field_data.content,
                confidence=field_data.confidence,
                coordinates=self.relative_coordinates_for(field_data),
            ),
        )

        return edata
