from pydantic import Field

from pixelemon.constants import INCHES_TO_MILLIMETERS
from pixelemon.optics._base_optical_assembly import BaseOpticalAssembly


class ArducamCS2316ZM02(BaseOpticalAssembly):
    image_circle_diameter: float = Field(default=1 / 2.3 * INCHES_TO_MILLIMETERS, frozen=True)
    focal_length: float = Field(default=16.0, frozen=True)
    focal_ratio: float = Field(default=1.2, frozen=True)
