# pixelemon

Citra's Python plate solver using Tetra3 via cedar-solve.

## Features
- Define and configure telescope sensors and optics
- Load and process FITS images
- Plate solve images using Tetra3

## Installation

Install via pip (requires Python 3.9+ and <3.13):

```bash
pip install pixelemon
```

Or for development:

```bash
git clone https://github.com/citra-space/pixelemon.git
cd pixelemon
pip install -e .[dev]
```

## Example Usage

```python
from pathlib import Path
from pixelemon.sensors import IMX174
from pixelemon.optics import WilliamsMiniCat51
from pixelemon import Telescope, TelescopeImage, TetraSolver

TetraSolver.high_memory() # IMPORTANT <----

sensor = IMX174()
optical_assembly = WilliamsMiniCat51()
telescope = Telescope(sensor=sensor, optics=optical_assembly)

img_path = Path("./local/2025-10-17-021315.fits")
image = TelescopeImage.from_fits_file(img_path, telescope)

image.crop(10.0) # optional
solve = image.plate_solve
```

## Requirements
- Python 3.9+
- [pydantic](https://pydantic-docs.helpmanual.io/)
- [cedar-solve](https://github.com/citra-space/cedar-solve)
- [sep](https://github.com/kbarbary/sep)
- [astropy](https://www.astropy.org/)

## License
MIT

## Authors
- Brandon Sexton <brandon@citra.space>
