from pydantic import BaseModel, Field

from pixelemon.constants import MICRO_TO_MILLI
from pixelemon.optics import BaseOpticalAssembly
from pixelemon.sensors import BaseSensor


class Telescope(BaseModel):
    sensor: BaseSensor = Field(..., description="The sensor used in the imaging system")
    optics: BaseOpticalAssembly = Field(..., description="The optical assembly of the imaging system")

    @property
    def diagonal_field_of_view(self) -> float:
        full_fov = self.optics.field_of_view
        ratio = self.sensor.sensor_diagonal / self.optics.image_circle_diameter
        return full_fov * ratio

    @property
    def horizontal_field_of_view(self) -> float:
        full_fov = self.optics.field_of_view
        ratio = self.sensor.sensor_width / self.optics.image_circle_diameter
        return full_fov * ratio

    @property
    def vertical_field_of_view(self) -> float:
        full_fov = self.optics.field_of_view
        ratio = self.sensor.sensor_height / self.optics.image_circle_diameter
        return full_fov * ratio

    @property
    def horizontal_pixel_scale(self) -> float:
        fov = self.horizontal_field_of_view
        ratio = self.sensor.pixel_width * MICRO_TO_MILLI / self.sensor.sensor_width
        deg_per_pixel = fov * ratio
        return deg_per_pixel

    @property
    def diagonal_pixel_scale(self) -> float:
        fov = self.diagonal_field_of_view
        ratio = self.sensor.pixel_diagonal * MICRO_TO_MILLI / self.sensor.sensor_diagonal
        deg_per_pixel = fov * ratio
        return deg_per_pixel

    @property
    def aspect_ratio(self) -> float:
        return self.sensor.sensor_width / self.sensor.sensor_height
