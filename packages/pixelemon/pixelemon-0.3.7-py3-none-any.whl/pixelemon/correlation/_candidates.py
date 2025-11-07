from pydantic import BaseModel, Field, RootModel


class CorrelationCandidate(BaseModel):
    id: str = Field(..., description="Unique identifier for the candidate")
    streak_length: float = Field(..., description="Length of the streak in pixels")
    angle_to_horizon: float = Field(..., description="Orientation angle of the streak in radians")
    x_centroid: float = Field(..., description="X coordinate of the streak centroid in pixels")
    y_centroid: float = Field(..., description="Y coordinate of the streak centroid in pixels")


class CorrelationCandidates(RootModel[list[CorrelationCandidate]]):

    def __len__(self) -> int:
        return len(self.root)

    def __getitem__(self, index: int) -> CorrelationCandidate:
        return self.root[index]

    def __iter__(self):
        return iter(self.root)
