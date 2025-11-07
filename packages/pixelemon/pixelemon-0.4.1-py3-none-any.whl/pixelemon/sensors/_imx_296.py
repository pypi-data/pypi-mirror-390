from pydantic import Field

from pixelemon.sensors._base_sensor import BaseSensor


class IMX296(BaseSensor):
    x_pixel_count: int = Field(default=1456, frozen=True)
    y_pixel_count: int = Field(default=1088, frozen=True)
    pixel_width: float = Field(default=3.4, frozen=True)
    pixel_height: float = Field(default=3.4, frozen=True)
