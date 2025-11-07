from pathlib import Path

import pytest

from pixelemon import Telescope, TelescopeImage
from pixelemon.optics import ArducamCS2325ZM01, ArducamM2508ZH02
from pixelemon.sensors import IMX296


@pytest.fixture
def raw_fits_path() -> Path:
    return Path("tests/test-imx296-8mm.fits")


@pytest.fixture
def telescope() -> Telescope:
    sensor = IMX296()
    optical_assembly = ArducamM2508ZH02()
    telescope = Telescope(sensor=sensor, optics=optical_assembly)
    return telescope


@pytest.fixture
def image(telescope: Telescope, raw_fits_path: Path) -> TelescopeImage:
    return TelescopeImage.from_fits_file(raw_fits_path, telescope)


def test_imx296_arducam_8mm_m12(telescope: Telescope):
    assert telescope.sensor == IMX296()
    assert telescope.optics == ArducamM2508ZH02()
    assert telescope.horizontal_field_of_view == pytest.approx(31.589, abs=0.001)
    assert telescope.vertical_field_of_view == pytest.approx(23.605, abs=0.001)
    assert telescope.diagonal_field_of_view == pytest.approx(39.434, abs=0.001)
    assert telescope.horizontal_pixel_scale == pytest.approx(78.104, abs=0.001)


def test_imx296_arducam_25mm_cs():
    sensor = IMX296()
    optical_assembly = ArducamCS2325ZM01()
    telescope = Telescope(sensor=sensor, optics=optical_assembly)

    assert telescope.sensor == sensor
    assert telescope.optics == optical_assembly
    assert telescope.horizontal_field_of_view == pytest.approx(11.166, abs=0.001)
    assert telescope.vertical_field_of_view == pytest.approx(8.344, abs=0.001)
    assert telescope.diagonal_field_of_view == pytest.approx(13.939, abs=0.001)
    assert telescope.horizontal_pixel_scale == pytest.approx(27.609, abs=0.001)


def test_detections(image: TelescopeImage):
    image.crop(10.0)
    image.remove_background()
    detections = image.detections
    assert len(detections) > 0


def test_load_fits_file(telescope: Telescope, raw_fits_path: Path):
    image = TelescopeImage.from_fits_file(raw_fits_path, telescope)
    assert image._original_array is not None
    assert image._processed_array is not None
    assert image.telescope is not None
    assert image._original_array.shape[0] == image.telescope.sensor.y_pixel_count
    assert image._original_array.shape[1] == image.telescope.sensor.x_pixel_count


def test_write_fits_file(image: TelescopeImage, tmp_path: Path):
    output_path = tmp_path / "output.fits"
    image.write_to_fits_file(output_path)
    assert output_path.exists()
