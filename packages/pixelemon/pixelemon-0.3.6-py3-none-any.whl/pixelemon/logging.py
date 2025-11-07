import logging

PIXELEMON_LOG = logging.getLogger(__name__)
PIXELEMON_LOG.setLevel(logging.INFO)


# set logger name
PIXELEMON_LOG.name = "pixelemon"

# format time to yyyy-mm-ddThh:mm:ss.sss
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
PIXELEMON_LOG.addHandler(handler)
