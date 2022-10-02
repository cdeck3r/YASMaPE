import json
import logging
import os
import sys
import time

import click
from celery import Celery, signature
from celery.states import state, PENDING, SUCCESS, STARTED 
from celery.app.log import TaskFormatter
from celery.utils.log import get_task_logger
from waiting import TimeoutExpired, wait

# Global vars
TIMEOUT_SECONDS = 2  # waiting time for task in status STARTED

# logger
logger = logging.getLogger(__name__)
sh = logging.StreamHandler()
sh.setFormatter(TaskFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.setLevel(logging.INFO)
logger.addHandler(sh)


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.option(
    '-v',
    '--verbose',
    is_flag=True,
    help='Show all extra arguments groups as key/value pairs, e.g. port / 5555',
)
@click.option(
    '-f',
    '--tidfile',
    help='File path to store the task id when task was successfully consumed',
)

@click.argument(
    'signature_file',
    required=True,
    type=click.File('r'),
    metavar='<signature_file>',
)
@click.argument(
    'queue',
    required=True,
    metavar='<queue>',
)
@click.pass_context
def cli(ctx, verbose, tidfile, signature_file, queue):
    """Submits a task from <signature_file> to <queue>"""
    
    # THE app is a celery instance with all parameters
    # from celeryconfig.py
    app = Celery()
    app.config_from_object('celeryconfig')
    
    # validate extra options
    if verbose:
        try:
            for i in range(0, len(ctx.args), 2):
                logger.info(
                    '{}. Keyword//Value: {} // {}'.format(
                        int(i / 2) + 1, ctx.args[i], ctx.args[i + 1]
                    )
                )
        except IndexError as ie:
            logger.error('{}. Keyword/Value: {}'.format(int(i / 2) + 1, ctx.args[i]))
            logger.error('Error: Keyword without value. Abort')
            sys.exit(os.EX_CONFIG)
    else:
        if len(ctx.args) % 2:
            logger.error('Error: Keyword and value counts do not match. Abort')
            sys.exit(os.EX_CONFIG)

    # We now know, we have a correct sets of key/value pairs
    keys = [ctx.args[i] for i in range(0, len(ctx.args), 2)]
    vals = [ctx.args[i + 1] for i in range(0, len(ctx.args), 2)]
    extra_args = dict(zip(keys, vals))

    all_args = [
        ('sig', signature_file),
        ('queue', queue),
        ('extra_args', extra_args),
    ]
    all_args_dict = dict(all_args)

    # it's all together, let's submit the celery task
    res_id = send_task(**all_args_dict)
    tid_record = { "tid" : res_id, "queue" : queue }
    # tidfile is a persistent information about the task 
    # it may help to query independently the task state
    write_tidfile(tid_record, tidfile)


def write_tidfile(tid_record, tidfile):
    try:
        with open(tidfile, 'w') as f:
            f.write(str(tid_record))
    except Exception as e:
        logger.error("Could not write file: {}".format(tidfile))
        sys.exit(os.EX_OSFILE)


def send_task(sig=None, queue=None, **kwargs):
    """Enqueue a task signature in queue
        
        Arguments:
        sig : can be a JSON string or a fp (a .read()-supporting text file or binary file containing a JSON document) 
        queue: name of the queue
        kwargs: extra_args when calling apply_async for signature 

    """

    # Load the signature json file, deserialize it,
    # and call signature remotely via celery
    json_sig = None
    try:
        json_sig = json.load(sig)
    except AttributeError:
        if isinstance(sig, (str, bytes, os.PathLike, int)) and os.path.isfile(sig):
            logger.error("Cannot read signature from file: {}".format(sig))
        else: 
            logger.warn("The provided signature is not a file. Will try string load.")
    try:
        json_sig = json.loads(sig)
    except TypeError:
        pass
    except json.JSONDecodeError:
        logger.error('Not a valid json string: {} '.format(sig))
        raise ValueError("Cannot work with provided signature.")
        
    # task signature
    tsig = signature(json_sig) 
    # call task signature
    # correct queue comes from task_routes in celeryconfig
    logger.info('Enqueue Task {} to queue {}'.format(tsig.task, queue))
    res = tsig.apply_async(queue=queue, kwargs=kwargs['extra_args'])

    # Check whether the consumption of this task was successful
    # Encapsulate this activity in a soft timeout (https://pypi.org/project/waiting/)
    try:
        wait(
            lambda: res.state >= state(STARTED),
            timeout_seconds=TIMEOUT_SECONDS,
            sleep_seconds=0.1,
            waiting_for=logger.debug(
                'Celery task consumption in queue {}'.format(queue)
            ),
        )
    except TimeoutExpired as te:
        logger.warning(te)
        logger.warning('Revoke task {} (id: {}) from queue {}'.format(tsig.task, res.id, queue))
        res.revoke()        
        sys.exit(os.EX_TEMPFAIL)

    logger.info('Task {} (id: {}) successfully consumed from queue {}'.format(tsig.task, res.id, queue))

    return res.id
    
    # logger.info("Result: {}".format(res.get()))

    #while not res.ready():
    #    time.sleep(1)
    #logger.info("Task done. Success was {}.".format(res.get()))


if __name__ == '__main__':
    cli()
