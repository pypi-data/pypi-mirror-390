import numpy as np
from numpy import typing as npt
from pydantic import BaseModel, Field, RootModel


class DetectionLine(BaseModel):
    slope: float = Field(..., description="Slope of the streak line")
    intercept: float = Field(..., description="Y-intercept of the streak line")
    length: float = Field(..., description="Length of the streak line in pixels")
    x_centroid: float = Field(..., description="X coordinate of the streak centroid in pixels")
    y_centroid: float = Field(..., description="Y coordinate of the streak centroid in pixels")

    def get_distance(self, x: float, y: float) -> float:
        """Calculate the perpendicular distance from a point to the streak line."""
        numerator = abs(self.slope * x - y + self.intercept)
        denominator = np.sqrt(self.slope**2 + 1)
        return numerator / denominator

    @property
    def x0(self) -> float:
        """Get the starting x coordinate of the streak line."""
        return self.x_centroid - (self.length / 2) / np.sqrt(1 + self.slope**2)

    @property
    def y0(self) -> float:
        """Get the starting y coordinate of the streak line."""
        return self.slope * self.x0 + self.intercept

    @property
    def x1(self) -> float:
        """Get the ending x coordinate of the streak line."""
        return self.x_centroid + (self.length / 2) / np.sqrt(1 + self.slope**2)

    @property
    def y1(self) -> float:
        """Get the ending y coordinate of the streak line."""
        return self.slope * self.x1 + self.intercept


class Detection(BaseModel):
    x_centroid: float = Field(..., description="X coordinate of the detection centroid in pixels")
    y_centroid: float = Field(..., description="Y coordinate of the detection centroid in pixels")
    semi_major_axis: float = Field(..., description="Semi-major axis of the detection in pixels")
    semi_minor_axis: float = Field(..., description="Semi-minor axis of the detection in pixels")
    angle_to_horizon: float = Field(..., description="Orientation angle of the detection in radians")
    total_flux: float = Field(..., description="Total flux of the detection in arbitrary units")
    instrumental_magnitude: float = Field(..., description="Instrumental magnitude of the detection")
    segmentation_index: int = Field(..., description="Index of the detection in the segmentation map")

    @classmethod
    def from_sep_object(cls, obj: dict) -> "Detection":
        return cls(
            x_centroid=obj["x"],
            y_centroid=obj["y"],
            semi_major_axis=obj["a"],
            semi_minor_axis=obj["b"],
            angle_to_horizon=obj["theta"],
            total_flux=obj["flux"],
            instrumental_magnitude=obj["inst_mag"],
            segmentation_index=obj["seg_idx"],
        )

    @property
    def elongation(self) -> float:
        return self.semi_major_axis / self.semi_minor_axis

    def get_visual_magnitude(self, zero_point: float) -> float:
        return self.instrumental_magnitude + zero_point


class Detections(RootModel[list[Detection]]):

    @classmethod
    def from_sep_extract(cls, objects) -> "Detections":
        detections = [Detection.from_sep_object(obj) for obj in objects]
        return cls(detections)

    def __len__(self) -> int:
        return len(self.root)

    def __getitem__(self, index: int) -> Detection:
        return self.root[index]

    def __iter__(self):
        return iter(self.root)

    def append(self, detection: Detection) -> None:
        self.root.append(detection)

    @property
    def y_x_array(self) -> npt.NDArray[np.float32]:
        return np.array([[det.y_centroid, det.x_centroid] for det in self.root], dtype=np.float32)

    @property
    def x_y_array(self) -> npt.NDArray[np.float32]:
        return np.array([[det.x_centroid, det.y_centroid] for det in self.root], dtype=np.float32)

    @property
    def elongation_array(self) -> npt.NDArray[np.float32]:
        return np.array(
            [det.semi_major_axis / det.semi_minor_axis for det in self.root],
            dtype=np.float32,
        )

    @property
    def elongation_sigma(self) -> float:
        elongations = self.elongation_array
        return float(np.std(elongations))

    @property
    def average_elongation(self) -> float:
        elongations = self.elongation_array
        return float(np.mean(elongations))

    @property
    def stars(self) -> "Detections":
        mean_elongation = self.average_elongation
        sigma_elongation = self.elongation_sigma
        star_detections = [det for det in self if det.elongation <= (mean_elongation + sigma_elongation)]
        return Detections(star_detections)

    @property
    def satellites(self) -> "Detections":
        mean_elongation = self.average_elongation
        sigma_elongation = self.elongation_sigma
        satellite_detections = [det for det in self if det.elongation > (mean_elongation + sigma_elongation * 3)]
        return Detections(satellite_detections)
