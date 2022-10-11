from director import config, task

import sys
import os
import time
import json

from celery import Celery, signature, current_app
from celery.app.log import TaskFormatter
from celery import states
from celery.utils.log import get_task_logger
from waiting import TimeoutExpired, wait

# import celery_send_task (first, add parent folder to sys.path)
sys.path.insert(1, os.path.join(sys.path[0], config.get("CELERY_SEND_TASK_DIR")))
from celery_send_task import send_task
from celery_send_task import write_tidfile

logger = get_task_logger(__name__)

# additional celery config
current_app.conf.update(task_track_started=True, 
task_serializer='json',
result_serializer='json',
accept_content =['json'],
timezone='Europe/Berlin',
enable_utc=True,
task_acks_late=False,
)

def compile_task_signature(task_name, queue, **kwargs):
    """Compiles a dict for send_task as parameter
    
    Parameter:
        - task_name:    name of task to run 
        - queue:        queue name to enqueue and route the task 
        - **kwargs:     assigned to extra_args of task
    """
    # by convention: task_name is used in task, queue and tid file

    # configure task signature
    s = signature(task_name)
    sig = json.dumps(dict(s))    
    # Due to json schema, the following kwargs are guaranteed:
    # - symbol
    # - yaml
    extra_args = kwargs['payload']
    
    # compile task signature config
    all_args = [
        ('sig', sig),
        ('queue', queue),
        ('extra_args', extra_args),
    ]
    all_args_dict = dict(all_args)
    logger.debug("send_task params: {}".format(all_args_dict))
    
    return all_args_dict


@task(name="download_stock_data")
def download_stock_data(*args, **kwargs):
    task_name = 'download_stock_data'
    queue = 'q_yasmape.' + task_name
    task_sig = compile_task_signature(task_name, queue, **kwargs)

    symbol = kwargs['payload']['symbol']
    data_dir = '/YASMaPE/data' # default data_dir
    tid_filepath = os.path.join(data_dir, symbol, task_name+'.tid')
    
    # send_task to queue
    try:
        tid = send_task(**task_sig)
        tid_record = { "tid" : tid, "queue" : queue }
        write_tidfile(tid_record, tid_filepath)
    except ValueError as ve:
        logger.error(ve)


@task(name="create_feature")
def create_feature(*args, **kwargs):
    pass

@task(name="ludwig_preprocess")
def ludwig_preprocess(*args, **kwargs):
    symbol = kwargs['payload']['symbol']
    yaml = kwargs['payload']['yaml']
    pass

@task(name="ludwig_train")
def ludwig_train(*args, **kwargs):
    symbol = kwargs['payload']['symbol']
    yaml = kwargs['payload']['yaml']

    pass

@task(name="ludwig_experiment")
def ludwig_experiment(*args, **kwargs):
    symbol = kwargs['payload']['symbol']
    yaml = kwargs['payload']['yaml']
    pass

@task(name="ludwig_evaluate")
def ludwig_evaluate(*args, **kwargs):
    symbol = kwargs['payload']['symbol']
    yaml = kwargs['payload']['yaml']
    pass

@task(name="ludwig_predict")
def ludwig_predict(*args, **kwargs):
    symbol = kwargs['payload']['symbol']
    yaml = kwargs['payload']['yaml']
    pass

@task(name="create_modelcard")
def create_modelcard(*args, **kwargs):
    symbol = kwargs['payload']['symbol']
    yaml = kwargs['payload']['yaml']
    pass
