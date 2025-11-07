from pydantic import Field

from pixelemon.optics._base_optical_assembly import BaseOpticalAssembly


class Goshyda35(BaseOpticalAssembly):
    image_circle_diameter: float = Field(default=1 / 2 * 25.4, frozen=True)
    focal_length: float = Field(default=35.0, frozen=True)
    focal_ratio: float = Field(default=1.6, frozen=True)
