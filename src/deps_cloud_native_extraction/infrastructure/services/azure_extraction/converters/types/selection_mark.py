from azure.ai.documentintelligence.models import (
    DocumentField,
    DocumentSelectionMarkState,
)
from deps_extracted_data import CheckboxValue, ExtractedData

from .abstract import AbstractConverter

__all__ = ["SelectionMarkConverter"]


class SelectionMarkConverter(AbstractConverter):
    def handles(self, field: DocumentField) -> bool:
        return field.value_selection_mark is not None

    def convert(
        self,
        edata: ExtractedData,
        field_code: str,
        field_data: DocumentField,
    ) -> ExtractedData:
        checkbox_value = (
            CheckboxValue.CHECKED
            if field_data.value_selection_mark == DocumentSelectionMarkState.SELECTED
            else CheckboxValue.UNCHECKED
        )

        edata.add_checkbox(
            checkbox=self.efield_factory.create_checkbox(
                field_code=field_code,
                value=checkbox_value,
                confidence=field_data.confidence,
                coordinates=self.relative_coordinates_for(field_data),
            ),
        )

        return edata
