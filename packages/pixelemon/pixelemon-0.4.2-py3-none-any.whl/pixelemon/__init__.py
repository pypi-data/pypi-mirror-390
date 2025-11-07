from pathlib import Path

from pixelemon._plate_solve import TetraSolver
from pixelemon._telescope import Telescope
from pixelemon._telescope_image import TelescopeImage

PIXELEMON_DIRECTORY = Path(__file__).parent.resolve()

__all__ = ["Telescope", "TelescopeImage", "TetraSolver"]
