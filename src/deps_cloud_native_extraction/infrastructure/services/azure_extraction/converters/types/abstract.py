from abc import ABC, abstractmethod

from azure.ai.documentintelligence.models import (
    AnalyzeResult,
    BoundingRegion,
    DocumentField,
    DocumentFieldSchema,
)
from deps_extracted_data import (
    Bbox,
    ExtractedData,
    ExtractedFieldFactory,
    FieldDataFactory,
    SourceBboxCoordinates,
)

from deps_cloud_native_extraction.infrastructure.proxies import UnifiedDataImage

__all__ = ["AbstractConverter"]

_MINIMAL_BBOX_SIZE = 1e-3
FieldCode = str


class AbstractConverter(ABC):
    fdata_factory = FieldDataFactory()
    efield_factory = ExtractedFieldFactory()

    def __init__(
        self,
        extractor_schema: dict[FieldCode, DocumentFieldSchema],
        azure_response: AnalyzeResult,
        unified_images: list[UnifiedDataImage],
    ) -> None:
        self._schema = extractor_schema
        self._response = azure_response
        self._unified_images = unified_images

    @abstractmethod
    def convert(
        self,
        edata: ExtractedData,
        field_code: str,
        field_data: DocumentField,
    ) -> ExtractedData:
        pass

    @abstractmethod
    def handles(self, field: DocumentField) -> bool:
        pass

    def relative_coordinates_for(self, field: DocumentField) -> list[SourceBboxCoordinates] | None:
        if not field.bounding_regions:
            return None

        region: BoundingRegion = field.bounding_regions[0]

        source_id = self._source_id_for(page_index=region.page_number)
        bbox = self._transform_polygon_to_bbox(page_idx=region.page_number, polygon=region.polygon)

        return [SourceBboxCoordinates(value=source_id, bboxes=[bbox])]

    def _source_id_for(self, page_index: int) -> str:
        page: UnifiedDataImage | None = next(filter(lambda img: img.page == page_index, self._unified_images), None)

        if page is None:
            raise RuntimeError(
                f"Azure response returned field from {page_index} page, "
                f"but there's no Unified Image was found for this page",
            )

        return page.id

    def _transform_polygon_to_bbox(self, page_idx: int, polygon: list[float]) -> Bbox:
        page_width, page_height = self._page_size(page_idx)

        relative_x = [x / page_width for x in polygon[::2]]
        relative_y = [y / page_height for y in polygon[1::2]]

        left_top_x = min(relative_x)
        left_top_y = min(relative_y)

        bbox_width = max(relative_x) - left_top_x
        bbox_height = max(relative_y) - left_top_y

        bbox_width = max(bbox_width, _MINIMAL_BBOX_SIZE)  # we don't want to have 0 width or height
        bbox_height = max(bbox_height, _MINIMAL_BBOX_SIZE)

        return Bbox(x=left_top_x, y=left_top_y, w=bbox_width, h=bbox_height)

    def _page_size(self, pg_number: int) -> tuple[float, float]:
        page = self._response.pages[pg_number - 1]

        return page.width, page.height
