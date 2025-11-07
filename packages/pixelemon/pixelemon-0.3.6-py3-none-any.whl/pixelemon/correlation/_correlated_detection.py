from pydantic import BaseModel


class CorrelatedDetection(BaseModel):
    satellite_id: str
    right_ascension: float
    declination: float
    magnitude: float
    length_difference: float
    angle_difference: float
    perpendicular_distance: float
    centroid_distance: float
