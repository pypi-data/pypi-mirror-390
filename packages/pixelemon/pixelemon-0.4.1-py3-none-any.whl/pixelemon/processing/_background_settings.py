from pydantic import BaseModel, Field

DEFAULT_BACKGROUND_MESH_COUNT = 30
MIN_BACKGROUND_MESH_COUNT = 10
MAX_BACKGROUND_MESH_COUNT = 100

DEFAULT_BACKGROUND_FILTER_SIZE = 2
MIN_BACKGROUND_FILTER_SIZE = 1
MAX_BACKGROUND_FILTER_SIZE = 10

DEFAULT_BACKGROUND_DETECTION_THRESHOLD = 1.0
MIN_BACKGROUND_DETECTION_THRESHOLD = 0.1
MAX_BACKGROUND_DETECTION_THRESHOLD = 6.0


class BackgroundSettings(BaseModel):
    mesh_count: int = Field(
        default=DEFAULT_BACKGROUND_MESH_COUNT,
        description="Number of meshes for background estimation",
        ge=MIN_BACKGROUND_MESH_COUNT,
        le=MAX_BACKGROUND_MESH_COUNT,
    )
    filter_size: int = Field(
        default=DEFAULT_BACKGROUND_FILTER_SIZE,
        description="Size of the filter for background smoothing",
        ge=MIN_BACKGROUND_FILTER_SIZE,
        le=MAX_BACKGROUND_FILTER_SIZE,
    )
    detection_threshold: float = Field(
        default=DEFAULT_BACKGROUND_DETECTION_THRESHOLD,
        description="Threshold for background detection",
        ge=MIN_BACKGROUND_DETECTION_THRESHOLD,
        le=MAX_BACKGROUND_DETECTION_THRESHOLD,
    )
