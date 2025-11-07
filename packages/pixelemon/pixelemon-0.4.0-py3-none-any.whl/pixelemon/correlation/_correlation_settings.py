from pydantic import BaseModel, Field

DEFAULT_CORRELATION_LENGTH_LIMIT = 3.0  # in pixels
DEFAULT_CORRELATION_ANGLE_LIMIT = 1.0  # in degrees


class CorrelationSettings(BaseModel):

    length_limit: float = Field(
        default=DEFAULT_CORRELATION_LENGTH_LIMIT,
        description="Maximum allowed length difference for correlation in pixels",
        ge=0.1,
    )
    angle_limit: float = Field(
        default=DEFAULT_CORRELATION_ANGLE_LIMIT,
        description="Maximum allowed angle difference for correlation in degrees",
        ge=0.1,
        le=180.0,
    )
