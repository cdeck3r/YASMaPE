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
task_acks_late = False
worker_prefetch_multiplier = 1
task_track_started = True

# it is True by default, but we want to be sure
task_create_missing_queues = True
