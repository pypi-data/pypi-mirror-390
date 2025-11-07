from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

import tetra3  # type: ignore
from pydantic import BaseModel, Field, model_validator

from pixelemon.logging import PIXELEMON_LOG

_GH_URL = "https://github.com/citra-space/pixelemon/releases/download/general-purpose-database"
TETRA_DB_NAME = "tyc_db_to_40_deg.npz"
TETRA_DATABASE_URL = f"{_GH_URL}/{TETRA_DB_NAME}"
TETRA_DATABASE_PATH = Path(__file__).parent / TETRA_DB_NAME


class TetraSolver(tetra3.Tetra3):

    _instance: "TetraSolver | None" = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> "TetraSolver":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, database_path: Path | None = None, reload: bool = False):
        if not self._initialized or reload:
            if database_path is None:
                super().__init__()
            else:
                super().__init__(load_database=database_path.as_posix())
            self.settings = TetraSettings.model_validate(self.database_properties)
            self._initialized = True

    @classmethod
    def low_memory(cls) -> "TetraSolver":
        solver = cls(reload=True)
        PIXELEMON_LOG.info("Configured TetraSolver for low memory usage")
        return solver

    @classmethod
    def high_memory(cls) -> "TetraSolver":
        if not TETRA_DATABASE_PATH.exists():
            PIXELEMON_LOG.warning("Tetra database not found locally.  One-time download may take several minutes.")
            PIXELEMON_LOG.info(f"Downloading Tetra database from {_GH_URL} to {TETRA_DATABASE_PATH}")
            urlretrieve(TETRA_DATABASE_URL, TETRA_DATABASE_PATH.as_posix())
        solver = cls(TETRA_DATABASE_PATH, reload=True)
        PIXELEMON_LOG.info("Configured TetraSolver for high memory usage")
        return solver


class TetraSettings(BaseModel):
    dimmest_star_magnitude: float = Field(
        ...,
        description="The dimmest star magnitude to consider in the plate solve",
        alias="star_max_magnitude",
    )
    max_field_of_view: float = Field(
        ...,
        description="The maximum field of view in degrees the solver can reliably handle",
        alias="max_fov",
    )
    min_field_of_view: float = Field(
        ...,
        description="The minimum field of view in degrees the solver can reliably handle",
        alias="min_fov",
    )
    verification_star_count: int = Field(
        ...,
        description="The number of stars to use for verification of the plate solve",
        alias="verification_stars_per_fov",
    )

    def model_post_init(self, _: Any) -> None:
        PIXELEMON_LOG.info(f"Tetra dimmest star magnitude set to {self.dimmest_star_magnitude}")
        PIXELEMON_LOG.info(f"Tetra max field of view set to {self.max_field_of_view} degrees")
        PIXELEMON_LOG.info(f"Tetra min field of view set to {self.min_field_of_view} degrees")
        PIXELEMON_LOG.info(f"Tetra verification star count set to {self.verification_star_count}")


class MatchedStar(BaseModel):
    right_ascension: float = Field(..., description="Right ascension in degrees")
    declination: float = Field(..., description="Declination in degrees")
    magnitude: float = Field(..., description="Visual magnitude")

    @model_validator(mode="before")
    def from_tuple(cls, vals):
        if not isinstance(vals, dict):
            return {"right_ascension": vals[0], "declination": vals[1], "magnitude": vals[2]}


class PlateSolve(BaseModel):
    right_ascension: float = Field(
        ...,
        description="Right Ascension in degrees",
        alias="RA",
    )
    declination: float = Field(
        ...,
        description="Declination in degrees",
        alias="Dec",
    )
    roll: float = Field(
        ...,
        description="Roll angle in degrees",
        alias="Roll",
    )
    estimated_horizontal_fov: float = Field(
        ...,
        description="Estimated horizontal field of view in degrees",
        alias="FOV",
    )
    root_mean_square_error: float = Field(
        ...,
        description="Root mean square error of the plate solve in arcseconds",
        alias="RMSE",
    )
    number_of_stars: int = Field(
        ...,
        description="Number of stars used in the plate solve",
        alias="Matches",
    )
    false_positive_probability: float = Field(
        ...,
        description="Probability of a false positive plate solve",
        alias="Prob",
    )
    solve_time: float = Field(
        ...,
        description="Time taken to perform the plate solve in milliseconds",
        alias="T_solve",
    )

    matched_stars: list[MatchedStar] = Field(
        ..., description="Collection of coordinates and magnitudes for matched stars in the solve"
    )
    distortion: float = Field(..., description="Calculated distortion of the image")
