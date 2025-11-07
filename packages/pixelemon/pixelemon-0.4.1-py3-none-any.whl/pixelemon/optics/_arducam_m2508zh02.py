from pydantic import Field

from pixelemon.optics._base_optical_assembly import BaseOpticalAssembly


class ArducamM2508ZH02(BaseOpticalAssembly):
    image_circle_diameter: float = Field(default=1 / 2.5 * 25.4, frozen=True)
    focal_length: float = Field(default=8.0, frozen=True)
    focal_ratio: float = Field(default=2.0, frozen=True)
