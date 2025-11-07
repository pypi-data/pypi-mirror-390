from datetime import datetime
from pathlib import Path

import numpy as np
import numpy.typing as npt
import sep  # type: ignore
from astropy.coordinates import SkyCoord  # type: ignore
from astropy.io import fits  # type: ignore
from astropy.wcs import WCS  # type: ignore
from astropy.wcs.utils import fit_wcs_from_points  # type: ignore
from keplemon.bodies import Constellation, Observatory
from keplemon.elements import TopocentricElements
from keplemon.enums import ReferenceFrame
from keplemon.time import Epoch, TimeSpan
from numpy.lib import recfunctions as rfn
from pydantic import BaseModel, Field

from pixelemon._plate_solve import PlateSolve, TetraSolver
from pixelemon._telescope import Telescope
from pixelemon.constants import BASE_TO_KILO, KILO_TO_BASE, PERCENT_TO_DECIMAL, SUN_MAGNITUDE
from pixelemon.correlation import CorrelatedDetection, CorrelationCandidate, CorrelationCandidates, CorrelationSettings
from pixelemon.logging import PIXELEMON_LOG
from pixelemon.processing import (
    MIN_BACKGROUND_MESH_COUNT,
    BackgroundSettings,
    Detection,
    DetectionLine,
    Detections,
    DetectionSettings,
)


class TelescopeImage(BaseModel):
    _original_array: npt.NDArray[np.float32] | None = None
    _processed_array: npt.NDArray[np.float32] | None = None
    _segmentation_map: npt.NDArray[np.int32] | None = None
    _plate_solve: PlateSolve | None = None
    _detections: Detections | None = None
    _background: sep.Background | None = None
    _background_removed: bool = False
    epoch: datetime | None = None
    telescope: Telescope | None = None
    exposure_time: float | None = None
    _ground_site: Observatory | None = None
    _wcs: WCS | None = None
    image_scale: float = Field(default=1.0, description="The image scale due to cropping")
    background_settings: BackgroundSettings = Field(default=BackgroundSettings())
    detection_settings: DetectionSettings = Field(default=DetectionSettings.streak_source_defaults())
    correlation_settings: CorrelationSettings = Field(default=CorrelationSettings())

    @classmethod
    def from_fits_file(cls, file_path: Path, telescope: Telescope) -> "TelescopeImage":
        with fits.open(file_path) as hdul:
            img = cls()
            assert hasattr(hdul[0], "header")
            header = getattr(hdul[0], "header")
            img.exposure_time = header["EXPTIME"]
            img._wcs = WCS(header)
            img.epoch = datetime.fromisoformat(header["DATE-OBS"])
            img.telescope = telescope
            img._original_array = getattr(hdul[0], "data").astype(np.float32)
            lon = header["OBSGEO-L"]
            lat = header["OBSGEO-B"]
            h = header["OBSGEO-H"] * BASE_TO_KILO
            img._ground_site = Observatory(lat, lon, h)
            assert img._original_array is not None
            actual_ratio = img._original_array.shape[1] / img._original_array.shape[0]
            if not np.isclose(img.telescope.aspect_ratio, actual_ratio, atol=1e-6):
                PIXELEMON_LOG.warning("Trimming image to match expected aspect")
                new_width = int(img._original_array.shape[0] * img.telescope.aspect_ratio)
                img._original_array = img._original_array[:, 0:new_width]
                img._original_array = np.ascontiguousarray(img._original_array)
            assert img._original_array is not None
            img._processed_array = img._original_array.copy()
        PIXELEMON_LOG.info(f"Loaded {img._original_array.shape} image from {file_path} with epoch {img.epoch}")
        return img

    def get_correlation_candidates(self, sats: Constellation) -> CorrelationCandidates:
        if self._ground_site is None:
            raise ValueError("Ground site is not set.")
        solve = self.plate_solve
        if solve is None:
            raise ValueError("Plate solve is not available.")
        if self.epoch is None:
            raise ValueError("Image epoch is not set.")
        if self.exposure_time is None:
            raise ValueError("Exposure time is not set.")

        kepoch = Epoch.from_datetime(self.epoch)
        half_exposure = TimeSpan.from_seconds(self.exposure_time / 2)

        fov_start = self._ground_site.get_field_of_view_report(
            kepoch - half_exposure,
            TopocentricElements.from_j2000(
                kepoch,
                solve.right_ascension,
                solve.declination,
            ),
            self.horizontal_field_of_view / 2,
            sats,
            ReferenceFrame.J2000,
        )

        fov_end = self._ground_site.get_field_of_view_report(
            kepoch + half_exposure,
            TopocentricElements.from_j2000(
                kepoch,
                solve.right_ascension,
                solve.declination,
            ),
            self.horizontal_field_of_view / 2,
            sats,
            ReferenceFrame.J2000,
        )

        end_fov_dict = {candidate.satellite_id: candidate for candidate in fov_end.candidates}
        correlation_candidates = CorrelationCandidates([])
        for start_candidate in fov_start.candidates:

            r = start_candidate.direction.range
            assert r is not None
            r = r * KILO_TO_BASE
            area = self.detection_settings.satellite_area
            albedo = self.detection_settings.satellite_albedo
            vis_mag = SUN_MAGNITUDE + 2.5 * np.log10((4 * np.pi * r**2) / (albedo * area))
            if start_candidate.satellite_id in end_fov_dict and vis_mag <= self.detection_settings.limiting_magnitude:
                fits_start = self.get_fits_pixels(
                    start_candidate.direction.right_ascension,
                    start_candidate.direction.declination,
                )
                end_candidate = end_fov_dict[start_candidate.satellite_id]
                fits_end = self.get_fits_pixels(
                    end_candidate.direction.right_ascension,
                    end_candidate.direction.declination,
                )
                streak_x_midpoint = (fits_start[0] + fits_end[0]) / 2
                streak_y_midpoint = (fits_start[1] + fits_end[1]) / 2
                streak_length = ((fits_end[0] - fits_start[0]) ** 2 + (fits_end[1] - fits_start[1]) ** 2) ** 0.5
                angle_to_horizon = np.arctan2(fits_end[1] - fits_start[1], fits_end[0] - fits_start[0])
                correlation_candidate = CorrelationCandidate(
                    id=start_candidate.satellite_id,
                    streak_length=streak_length + self.detection_settings.full_width_half_maximum,
                    angle_to_horizon=angle_to_horizon,
                    x_centroid=streak_x_midpoint,
                    y_centroid=streak_y_midpoint,
                )
                correlation_candidates.root.append(correlation_candidate)

        PIXELEMON_LOG.info(
            f"Generated {len(correlation_candidates)} correlation candidates from {sats.count} satellites"
        )
        return correlation_candidates

    def get_angular_distance(self, x0: float, y0: float, x1: float, y1: float) -> float:
        if self._wcs is None:
            raise ValueError("WCS is not set.")
        sky0 = self._wcs.pixel_to_world(x0, y0)
        sky1 = self._wcs.pixel_to_world(x1, y1)
        return sky0.separation(sky1).deg

    def get_angles(self, x: float, y: float) -> tuple[float, float]:
        if self._wcs is None:
            raise ValueError("WCS is not set.")
        sky = self._wcs.pixel_to_world(x, y)
        return sky.ra.deg, sky.dec.deg

    def get_correlation_to_candidate(self, candidate: CorrelationCandidate) -> CorrelatedDetection | None:
        detections = self.detections.satellites
        if len(detections) == 0:
            return None

        centroid_distances = []
        angular_differences = []
        perpendicular_distances = []
        length_differences = []

        for det in detections:
            streak_line = self.get_streak_line(det)
            centroid_distances.append(
                ((candidate.x_centroid - det.x_centroid) ** 2 + (candidate.y_centroid - det.y_centroid) ** 2) ** 0.5
            )
            angle_diff = abs(candidate.angle_to_horizon - det.angle_to_horizon)
            angle_diff = min(angle_diff, np.pi - angle_diff)
            angular_differences.append(angle_diff)
            perpendicular_distances.append(streak_line.get_distance(candidate.x_centroid, candidate.y_centroid))
            length_differences.append(abs(candidate.streak_length - streak_line.length))

        best_centroid = int(np.argmin(centroid_distances))
        best_angular = int(np.argmin(angular_differences))
        best_perpendicular = int(np.argmin(perpendicular_distances))
        best_length = int(np.argmin(length_differences))

        ang_limit = np.deg2rad(self.correlation_settings.angle_limit)
        len_limit = self.correlation_settings.length_limit

        # take the best match if all methods agree
        if (
            best_angular == best_centroid == best_perpendicular == best_length
            and length_differences[best_length] <= len_limit
            and angular_differences[best_angular] <= ang_limit
        ):
            best_i = best_centroid

        # use angle if length is in tolerance
        elif length_differences[best_angular] <= len_limit and angular_differences[best_angular] <= ang_limit:
            best_i = best_angular

        # use length if angle is in tolerance
        elif angular_differences[best_length] <= ang_limit and length_differences[best_length] <= len_limit:
            best_i = best_length

        else:
            best_i = -1

        ra_dec = self.get_angles(det.x_centroid, det.y_centroid)
        zp = self.zero_point
        assert zp is not None

        if best_i >= 0:
            return CorrelatedDetection(
                satellite_id=candidate.id,
                right_ascension=ra_dec[0],
                declination=ra_dec[1],
                magnitude=det.get_visual_magnitude(zp),
                length_difference=length_differences[best_i],
                angle_difference=np.rad2deg(angular_differences[best_i]),
                perpendicular_distance=perpendicular_distances[best_i],
                centroid_distance=centroid_distances[best_i],
            )
        else:
            return None

    def get_correlation_to_detection(self, det: Detection, sats: CorrelationCandidates) -> CorrelatedDetection | None:
        streak_angle = -det.angle_to_horizon
        xc, yc = det.x_centroid, self.height - 1 - det.y_centroid
        streak_line = self.get_streak_line(det)

        centroid_distances = []
        perpendicular_distances = []
        angle_differences = []
        length_differences = []
        angular_distances = []

        for candidate in sats:
            angular_distances.append(self.get_angular_distance(xc, yc, candidate.x_centroid, candidate.y_centroid))
            length_differences.append(abs(candidate.streak_length - streak_line.length))
            angle_diff = abs(candidate.angle_to_horizon - streak_angle)
            angle_diff = min(angle_diff, np.pi - angle_diff)
            angle_differences.append(angle_diff)
            centroid_distances.append(((candidate.x_centroid - xc) ** 2 + (candidate.y_centroid - yc) ** 2) ** 0.5)
            perpendicular_distances.append(streak_line.get_distance(candidate.x_centroid, candidate.y_centroid))

        best_by_centroid = int(np.argmin(centroid_distances))
        best_by_angle = int(np.argmin(angle_differences))
        best_by_length = int(np.argmin(length_differences))
        best_by_distance = int(np.argmin(perpendicular_distances))

        ang_limit = np.deg2rad(self.correlation_settings.angle_limit)
        len_limit = self.correlation_settings.length_limit

        if (
            best_by_centroid == best_by_angle == best_by_length == best_by_distance
            and length_differences[best_by_length] <= len_limit
            and angle_differences[best_by_length] <= ang_limit
        ):
            best_i = best_by_centroid

        elif length_differences[best_by_angle] <= len_limit and angle_differences[best_by_angle] <= ang_limit:
            best_i = best_by_angle

        elif angle_differences[best_by_length] <= ang_limit and length_differences[best_by_length] <= len_limit:
            best_i = best_by_length

        else:
            best_i = -1

        if best_i >= 0:
            candidate = sats[best_i]
            ra_dec = self.get_angles(det.x_centroid, det.y_centroid)
            zp = self.zero_point
            assert zp is not None
            return CorrelatedDetection(
                satellite_id=candidate.id,
                right_ascension=ra_dec[0],
                declination=ra_dec[1],
                magnitude=det.get_visual_magnitude(zp),
                length_difference=length_differences[best_i],
                angle_difference=np.rad2deg(angle_differences[best_i]),
                perpendicular_distance=perpendicular_distances[best_i],
                centroid_distance=centroid_distances[best_i],
            )
        else:
            return None

    def get_mask(self, detection: Detection) -> npt.NDArray[np.int32]:
        if self._segmentation_map is None:
            raise ValueError("Segmentation map is not available. Run detection first.")
        return (self._segmentation_map == detection.segmentation_index).astype(np.int32)

    def get_streak_line(self, detection: Detection) -> DetectionLine:
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        mask = self.get_mask(detection)
        y_indices, x_indices = np.nonzero(mask)
        y_indices = self.height - 1 - y_indices

        if len(x_indices) < 2:
            raise ValueError("Not enough points to fit a line.")
        a_mat = np.vstack([x_indices, np.ones(len(x_indices))]).T
        m, b = np.linalg.lstsq(a_mat, y_indices, rcond=None)[0]

        x0 = x_indices.min()
        y0 = m * x0 + b
        x1 = x_indices.max()
        y1 = m * x1 + b
        length = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5

        return DetectionLine(
            slope=m,
            intercept=b,
            length=length,
            x_centroid=detection.x_centroid,
            y_centroid=detection.y_centroid,
        )

    def get_streak_length(self, detection: Detection) -> float:
        streak_line = self.get_streak_line(detection)
        return streak_line.length

    def get_fits_line(self, detection: Detection) -> tuple[tuple[float, float], tuple[float, float]]:
        xc, yc = detection.x_centroid, self.height - 1 - detection.y_centroid
        theta = detection.angle_to_horizon

        length = self.get_streak_length(detection)
        dx = (length / 2) * np.cos(theta)
        dy = (length / 2) * np.sin(-theta)
        return (xc - dx, yc - dy), (xc + dx, yc + dy)

    def get_fits_circle(self, detection: Detection) -> tuple[tuple[float, float], tuple[float, float]]:
        xc, yc = detection.x_centroid, self.height - 1 - detection.y_centroid
        r = self.get_streak_length(detection) / 2
        return (xc - r, yc - r), (xc + r, yc + r)

    def write_to_fits_file(self, file_path: Path):
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        fits.writeto(file_path, self._processed_array.astype("uint8"), overwrite=True)
        PIXELEMON_LOG.info(f"Saved processed image to {file_path}")

    def crop(self, crop_percent: float):
        if self._original_array is None:
            raise ValueError("Image array is not loaded.")

        crop_fraction = crop_percent * PERCENT_TO_DECIMAL
        height, width = self._original_array.shape
        crop_height = int(height * crop_fraction / 2)
        crop_width = int(width * crop_fraction / 2)
        self._processed_array = np.ascontiguousarray(
            self._original_array[crop_height : height - crop_height, crop_width : width - crop_width]
        )
        PIXELEMON_LOG.info(f"Image cropped to {self._processed_array.shape}")
        self.image_scale = self.image_scale * (1.0 - crop_fraction)
        new_fov = f"{self.horizontal_field_of_view:.2f} x {self.vertical_field_of_view:.2f} degrees"  # noqa: E231
        PIXELEMON_LOG.info(f"New field of view is {new_fov}")
        self._plate_solve = None
        self._detections = None
        self._segmentation_map = None
        self._background = None
        self._background_removed = False

    def get_brightest_stars(self, count: int) -> Detections:
        detections = self.detections.stars
        sorted_detections = sorted(detections, key=lambda det: det.total_flux, reverse=True)
        return_count = min(count, len(sorted_detections))
        return Detections(sorted_detections[:return_count])

    @property
    def background(self) -> sep.Background:
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")

        if self._background is None:

            bw = max(
                MIN_BACKGROUND_MESH_COUNT, int(self._processed_array.shape[1] / self.background_settings.mesh_count)
            )
            bh = max(
                MIN_BACKGROUND_MESH_COUNT, int(self._processed_array.shape[0] / self.background_settings.mesh_count)
            )
            PIXELEMON_LOG.info(f"Background mesh size: {bw}x{bh}")

            self._background = sep.Background(
                self._processed_array,
                bw=bw,
                bh=bh,
                fw=self.background_settings.filter_size,
                fh=self.background_settings.filter_size,
                fthresh=self.background_settings.detection_threshold,
            )

        return self._background

    def remove_background(self):
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        self._processed_array = self._processed_array - self.background
        self._background_removed = True

    def reset(self):
        if self._original_array is None:
            raise ValueError("Image array is not loaded.")
        self._processed_array = self._original_array.copy()
        self.image_scale = 1.0
        self._background = None
        self._detections = None
        self._plate_solve = None
        self._background_removed = False
        self._segmentation_map = None
        PIXELEMON_LOG.info("Image reset to original")

    def get_fits_pixels(self, ra: float, dec: float) -> tuple[float, float]:
        if self._wcs is None:
            raise ValueError("WCS is not set.")
        sky = SkyCoord(ra, dec, unit="deg")
        return self._wcs.world_to_pixel(sky)

    def get_nearest_star(self, ra: float, dec: float) -> Detection:
        x, y = self.get_fits_pixels(ra, dec)
        h = self.height
        detections = self.detections.stars
        if len(detections) == 0:
            raise ValueError("No star detections available.")
        distances = [((det.x_centroid - x) ** 2 + (h - 1 - det.y_centroid - y) ** 2) ** 0.5 for det in detections]
        nearest_index = int(np.argmin(distances))
        return detections[nearest_index]

    @property
    def horizontal_field_of_view(self) -> float:
        if self.telescope is None:
            raise ValueError("Telescope is not set.")
        return self.telescope.horizontal_field_of_view * self.image_scale

    @property
    def vertical_field_of_view(self) -> float:
        if self.telescope is None:
            raise ValueError("Telescope is not set.")
        return self.telescope.vertical_field_of_view * self.image_scale

    @property
    def diagonal_field_of_view(self) -> float:
        if self.telescope is None:
            raise ValueError("Telescope is not set.")
        return self.telescope.diagonal_field_of_view * self.image_scale

    @property
    def detections(self):
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")

        if self._detections is None:
            objects, self._segmentation_map = sep.extract(
                self._processed_array,
                thresh=self.detection_settings.detection_threshold_sigma * self.background.globalrms,
                minarea=self.detection_settings.min_pixel_count,
                filter_kernel=self.detection_settings.gaussian_kernel,
                deblend_nthresh=self.detection_settings.deblend_mesh_count,
                deblend_cont=self.detection_settings.deblend_contrast,
                clean=self.detection_settings.merge_small_detections,
                segmentation_map=True,
            )

            # add instrumental magnitude to the objects
            instrumental_mag = -2.5 * np.log10(objects["flux"] / self.exposure_time)
            objects = rfn.append_fields(objects, "inst_mag", instrumental_mag, usemask=False)

            # add segmentation index to the objects
            seg_idx = np.arange(1, len(objects) + 1, dtype=np.int32)
            objects = rfn.append_fields(objects, "seg_idx", seg_idx, usemask=False)

            self._detections = Detections.from_sep_extract(objects)

        return self._detections

    @property
    def plate_solve(self) -> PlateSolve | None:
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        if self.telescope is None:
            raise ValueError("Telescope is not set.")

        if not self._background_removed:
            self.remove_background()

        if self._plate_solve is None:

            fov = f"{self.horizontal_field_of_view:.2f} x {self.vertical_field_of_view:.2f} degrees"  # noqa: E231
            PIXELEMON_LOG.info(f"Solving {len(self.detections.stars)} detected stars and FOV of {fov}")

            tetra_solve = TetraSolver().solve_from_centroids(
                self.get_brightest_stars(TetraSolver().settings.verification_star_count).y_x_array,
                size=self._processed_array.shape,
                fov_estimate=self.diagonal_field_of_view,
                return_matches=True,
            )

            if tetra_solve["RA"] is None:
                PIXELEMON_LOG.warning("Plate solve failed.")
                return None
            else:
                plate_solve = PlateSolve.model_validate(tetra_solve)
                pixel_scale = self.telescope.horizontal_pixel_scale
                assert self._wcs is not None

                # seed the WCS to improve chances of solution with fit_wcs_from_points
                self._wcs.wcs.crpix = [self._processed_array.shape[1] / 2, self._processed_array.shape[0] / 2]
                self._wcs.wcs.crval = [plate_solve.right_ascension, plate_solve.declination]
                self._wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
                self._wcs.wcs.cunit = ["deg", "deg"]
                theta = np.deg2rad(-plate_solve.roll)
                cd11 = -pixel_scale * np.cos(theta)
                cd12 = pixel_scale * np.sin(theta)
                cd21 = pixel_scale * np.sin(theta)
                cd22 = pixel_scale * np.cos(theta)
                self._wcs.wcs.cd = np.array([[cd11, cd12], [cd21, cd22]], dtype=float)

                # invert matched centroids for WCS fitting
                yx = np.array(tetra_solve["matched_centroids"])
                x, y = yx[:, 1], self.height - 1 - yx[:, 0]
                ra_dec = np.array(tetra_solve["matched_stars"])

                # fit WCS from matched stars
                sky = SkyCoord(ra=ra_dec[:, 0], dec=ra_dec[:, 1], unit="deg")
                self._wcs = fit_wcs_from_points((x, y), sky, sip_degree=5, proj_point="center")
                self._plate_solve = plate_solve

        return self._plate_solve

    @property
    def height(self) -> int:
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        return self._processed_array.shape[0]

    @property
    def zero_point(self) -> float | None:
        solve = self.plate_solve
        if solve is None:
            return None

        offsets = []
        for star in solve.matched_stars:
            detection = self.get_nearest_star(star.right_ascension, star.declination)
            offsets.append(star.magnitude - detection.instrumental_magnitude)

        if offsets:
            return float(np.mean(offsets))
        else:
            return None
