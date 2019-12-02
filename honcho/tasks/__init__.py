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


def import_task(name):
    task = __import__('honcho.tasks.{0}'.format(name), fromlist=[None])

    return task
