from math import atan, degrees

from pydantic import BaseModel, Field


class BaseOpticalAssembly(BaseModel):

    image_circle_diameter: float = Field(..., description="The diameter of the image circle in millimeters")
    focal_length: float = Field(..., description="The focal length of the optical assembly in millimeters")
    focal_ratio: float = Field(..., description="The focal ratio (f-number) of the optical assembly")

    @property
    def field_of_view(self) -> float:
        return degrees(2 * atan(self.image_circle_diameter / (2 * self.focal_length)))
