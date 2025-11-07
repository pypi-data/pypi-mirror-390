from math import sqrt

from pydantic import BaseModel, Field

from pixelemon.constants import MICRO_TO_MILLI


class BaseSensor(BaseModel):

    x_pixel_count: int = Field(..., description="The number of pixels in the horizontal direction")
    y_pixel_count: int = Field(..., description="The number of pixels in the vertical direction")
    pixel_width: float = Field(..., description="The width of each pixel in micrometers")
    pixel_height: float = Field(..., description="The height of each pixel in micrometers")

    @property
    def sensor_width(self) -> float:
        return self.x_pixel_count * self.pixel_width * MICRO_TO_MILLI

    @property
    def sensor_height(self) -> float:
        return self.y_pixel_count * self.pixel_height * MICRO_TO_MILLI

    @property
    def sensor_diagonal(self) -> float:
        return sqrt((self.sensor_width * self.sensor_width) + (self.sensor_height * self.sensor_height))

    @property
    def pixel_diagonal(self) -> float:
        return sqrt((self.pixel_width * self.pixel_width) + (self.pixel_height * self.pixel_height))
