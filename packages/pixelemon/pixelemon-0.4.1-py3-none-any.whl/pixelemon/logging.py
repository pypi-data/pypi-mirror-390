import logging
import sys
import warnings

from astropy.utils.exceptions import AstropyUserWarning, AstropyWarning  # type: ignore
from astropy.wcs import FITSFixedWarning  # type: ignore

COLORS = {
    "DEBUG": "\033[36m",  # cyan
    "INFO": "\033[32m",  # green
    "WARNING": "\033[33m",  # yellow
    "ERROR": "\033[31m",  # red
    "CRITICAL": "\033[1;31m",  # bold red
}
RESET = "\033[0m"

logging.basicConfig(
    level=logging.CRITICAL,
    force=True,  # Python 3.8+: replace existing handlers
)

logging.getLogger("astropy").setLevel(logging.CRITICAL + 1)
logging.getLogger("astropy").disabled = True

warnings.filterwarnings("ignore", category=AstropyWarning)
warnings.filterwarnings("ignore", category=AstropyUserWarning)
warnings.filterwarnings("ignore", category=FITSFixedWarning)


class LevelColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = COLORS.get(record.levelname, "")
        levelname_colored = f"{color}{record.levelname}{RESET}"
        record.levelname = levelname_colored
        return super().format(record)


def setup_logger(level=logging.INFO):

    pkg = __name__.split(".")[0]
    logger = logging.getLogger(pkg)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        fmt = "%(asctime)s.%(msecs)03d: [%(levelname)s] %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        h.setFormatter(LevelColorFormatter(fmt=fmt, datefmt=datefmt))
        logger.addHandler(h)

    return logger


PIXELEMON_LOG = setup_logger()
