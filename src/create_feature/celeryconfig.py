import os

# broker and result backend defined
# in the docker container by docker-compose

broker_url = os.environ['BROKER_URL']
result_backend = os.environ['RESULT_BACKEND']

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Berlin'
enable_utc = True

# avoid concurrency
# workers’ default prefetch count = worker_concurrency * worker_prefetch_multiplier
# ack task after it has been executed
# https://docs.celeryproject.org/en/stable/userguide/configuration.html#task-acks-late
# disable prefetching
# https://docs.celeryproject.org/en/stable/userguide/configuration.html#worker-prefetch-multiplier
# Activate STARTED state for task when executed by worker
# https://docs.celeryproject.org/en/stable/userguide/configuration.html#task-track-started
worker_concurrency = 1
optimization = 'fair'
task_acks_late = False  # ack when consumed, if True, ack returned after task has been successfully run
worker_prefetch_multiplier = 1
task_track_started = True

# queues to consume from
# see https://docs.celeryproject.org/en/stable/userguide/configuration.html#task-queues
task_queues = {
    'q_jupyter.create_feature': {
        'exchange': 'create_feature',
        'routing_key': 'create_feature',
    },
}

# Routing Understanding:
# if one calls a task with name 'create_feature',
# it will be published in queue 'q_jupyter.create_feature'
task_routes = {
    'create_feature': {'queue': 'q_jupyter.create_feature'},
}

# it is True by default, but we want to be sure
task_create_missing_queues = True
