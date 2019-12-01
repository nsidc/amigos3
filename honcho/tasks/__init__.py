from . import aquadopp  # noqa
from . import binex  # noqa
from . import camera  # noqa
from . import cr1000x  # noqa
from . import dts  # noqa
from . import monitor  # noqa
from . import orders  # noqa
from . import sbd  # noqa
from . import seabird  # noqa
from . import solar  # noqa
from . import archive  # noqa
from . import vaisala  # noqa

from honcho.util import ensure_dirs
from honcho.config import (
    DATA_DIR,
    DATA_TAGS,
    SBD_QUEUE_DIR,
    ORDERS_DIR,
    RESULTS_DIR,
    DTS_RAW_DATA_DIR,
    STAGED_UPLOAD_DIR,
)

ensure_dirs(
    [DATA_DIR(tag) for tag in DATA_TAGS]
    + [SBD_QUEUE_DIR(tag) for tag in DATA_TAGS]
    + [ORDERS_DIR, RESULTS_DIR, DTS_RAW_DATA_DIR, STAGED_UPLOAD_DIR]
)
