import os
import json
import logging
import traceback
from functools import wraps
from inspect import getmodule
from datetime import datetime

from honcho.config import EXECUTION_LOG_FILEPATH, TIMESTAMP_FMT
from honcho.util import format_timedelta, total_seconds


def task(func):
    '''
    Decorator that does basic logging and error handling for honcho tasks
    '''
    module_name = getmodule(func).__name__
    func_name = module_name + '.' + func.__name__

    @wraps(func)
    def wrapped(*args, **kwargs):
        logger = logging.getLogger(__name__)

        # Attempt task
        logger.info('Running {0}'.format(func_name))
        start = datetime.now()
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception:
            result = None
            success = False
            error_traceback = traceback.format_exc()

        run_time = datetime.now() - start
        logger.info(
            'Execution of {0} {1} after {2}'.format(
                func_name,
                'succeeded' if success else 'failed',
                format_timedelta(run_time),
            )
        )
        if not success:
            logger.error(error_traceback)

        # Load existing execution log data
        log_filepath = EXECUTION_LOG_FILEPATH(module_name)
        if os.path.exists(log_filepath):
            with open(log_filepath, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = {}

        # Update
        count_key = 'successes' if success else 'failures'
        average_key = 'success_runtime' if success else 'failure_runtime'
        last_key = 'last_success' if success else 'last_failure'
        n = log_data.get(count_key, 0)
        avg = log_data.get(average_key, 0)
        log_data[average_key] = (avg * n + total_seconds(run_time)) / (n + 1)
        log_data[count_key] = n + 1
        log_data[last_key] = start.strftime(TIMESTAMP_FMT)

        # Dump log data
        with open(log_filepath, 'w') as f:
            json.dump(log_data, f)

        return result

    return wrapped
