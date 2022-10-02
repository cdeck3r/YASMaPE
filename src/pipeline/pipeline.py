"""YASMaPE pipeline

"""

import json
import logging
import os
import sys
import time

from celery import Celery, signature
from celery.app.log import TaskFormatter
from celery.utils.log import get_task_logger
from waiting import TimeoutExpired, wait

# add parent folder to sys.path
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from celery_send_task.celery_send_task import send_task
from celery_send_task.celery_send_task import write_tidfile

# logger
logger = logging.getLogger(__name__)
sh = logging.StreamHandler()
sh.setFormatter(TaskFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.setLevel(logging.INFO)
logger.addHandler(sh)


####################
# pipeline steps
####################

def download_stock_data():
    pass

def create_feature():
    pass

def ludwig_preprocess():
    pass

def ludwig_train():
    pass

def ludwig_evaluate():
    pass

def ludwig_train():
    pass

####################

def pipeline():
    pass


if __name__ == '__main__':
    pipeline()