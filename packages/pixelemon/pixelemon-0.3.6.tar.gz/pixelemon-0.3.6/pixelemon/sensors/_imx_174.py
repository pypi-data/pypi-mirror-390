from pydantic import Field

from pixelemon.sensors._base_sensor import BaseSensor


class IMX174(BaseSensor):
    x_pixel_count: int = Field(default=1920, frozen=True)
    y_pixel_count: int = Field(default=1200, frozen=True)
    pixel_width: float = Field(default=5.86, frozen=True)
    pixel_height: float = Field(default=5.86, frozen=True)
