import os
import time
import traceback
from datetime import datetime

import pytz
from celery import states
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger
from worker import app

logger = get_task_logger(__name__)
this_dir = os.path.dirname(os.path.abspath(__file__))

from SKWorkflow import SKWorkflow

class TaskFailure(Exception):
    """Generic Task Exception

    Can be raised everywhere in a celery task.
    Reports only some fundamental information:
        1. error log message on the worker
        2. Caller receives some details from the exception provided to this class
        a) type of the provided exception exc
        b) exception's exc argument message

    Finally, it sets the task to FAILURE state
    and it ignores any other change to its properties.

    """

    def __init__(self, task, exc, message):
        super().__init__(message)
        logger.error(message)

        task.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(exc).__name__,
                'exc_message': str(exc),
                'custom': message,
            },
        )
        raise Ignore()

@app.task(bind=True, name='create_feature', queue='q_jupyter.create_feature')
def create_feature(self, **kwargs):
    """Starts the snakemake workflow for create_feature
    
    See the implementation of SKWorkflow class, what parameters
    are supported.
    """
    logger.info("Run task: {} from queue {}".format(self.__name__, self.queue))
    # warm-up to let caller see task state "STARTED"
    time.sleep(1)

    # some debugging
    tz = pytz.timezone(app.conf.timezone)
    now = datetime.now(tz)
    logger.debug('tasks.create_feature called at {}'.format(now))
    logger.debug('Params: {}'.format(kwargs))

    # configure and run snakemake workflow
    try:
        skw = SKWorkflow(logger)
        skw.config_workflow(kwargs)
        sk = skw.run_workflow()
    except Exception as e:
        raise TaskFailure(self, e, "Exception when running snakemake workflow")

    return sk  # True/False
