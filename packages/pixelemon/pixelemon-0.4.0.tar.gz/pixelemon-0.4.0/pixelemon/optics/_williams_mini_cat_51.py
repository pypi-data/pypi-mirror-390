from pydantic import Field

from pixelemon.optics._base_optical_assembly import BaseOpticalAssembly


class WilliamsMiniCat51(BaseOpticalAssembly):
    image_circle_diameter: float = Field(default=43.2, frozen=True)
    focal_length: float = Field(default=178.0, frozen=True)
    focal_ratio: float = Field(default=3.5, frozen=True)
