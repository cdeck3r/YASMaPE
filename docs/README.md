# YASMaPE Documentation 

This page collects all documentation ressource for YASMaPE.

_tbd. insert toc_

## YASMaPE Problem Formulation

YASMaPE experiments investigate a regression and a classification problem. Both are illustrated below.

**Regression problem:** Given the input feature vector, what is the predicted return?

![Return regression problem](regression_problem.png)

**Binary classification problem:** Given the input feature vector, is the predicted return larger than a given value?

![Return binary classification problem](classification_problem.png)

## Results

We will track results on a [separate page](results.md) using [modelcards](https://www.verifyml.com/).

## Feature Engineering

_windowing, etc._


## Machine Learning (ML) Pipeline

The pipeline's stages is shown as an activity diagram in the next figure.

_TODO insert image ![ac_pipeline.uml]()_

The software parts run independently in docker containers. They share their data via the filesystem. For coordination among the containers, they setup tasks queues using [celery](https://docs.celeryq.dev/en/stable/) as a distributed task queuing system. A [snakemake](https://snakemake.readthedocs.io/en/stable/) installation within each container executes the tasks consumed from the queue. Tasks become idempotent with snakemake.

The following UML component diagram shows the project's ML pipeline. 

_TODO insert image ![cp_pipeline.uml]()_

YASMaPE runs lots of experiments. We use [mlflow](https://mlflow.org/) for ML lifecycle management and experiment tracking.

### Coordination across Containers

Software components run in docker containers. Coordination runs task distributed [celery](https://docs.celeryq.dev/en/stable/) as a task queuing system. It utilize [rabbitmq](https://www.rabbitmq.com/) to distribute tasks to workers and to enable the distributed coordination. Using celery a workflow in one container can start a workflow in other container.

A celery worker encapsulates a snakemake workflow. `send_task` submits a task signature as argument into a celery queue running on the rabbitmq broker. It routes the task to the suitable worker, which consumes it from the queue and starts the workflow. Notice the asynchronous behavior, i.e. `send_task` does not wait for the workflow to complete.

The following figure depicts the coordination behavior for the pipeline's `create_feature` stage.

_TODO insert image ![seq_coordination.uml]()_

With snakemake come interesting features for running workflows asynchronously across containers:

* If the same snakemake workflow runs in series one after another run, all runs, but the first one, have no effect.
* If the workflow is invoked multiple times at the same time, the lock will avoid that any two Snakemake instances will want to create the same output file. See [snakemake FAQ](https://snakemake.readthedocs.io/en/stable/project_info/faq.html#how-does-snakemake-lock-the-working-directory).

Furthermore, the differnt celery workers are separated by different queues. A queue is only shared by workers for the same workflow. Each worker can only process one task at a time. A task submitted when the worker is still processing will remain in the queue as long as there is no other worker consuming from the same queue. `send_task` will observe that a task is consumed within a configured timeout after submission. If not, it will revoke the task from the queue. This will avoid a queue fillup. 

Horizotal scaling by spinning up more container with workers for the same workflow is possible.

### Orchestration

While one can enqueue each task step manually using the `src/celery_send_task/celery_send_task.py` script, orchestration organizes the sequence of steps within a pipeline or workflow.

The pipeline steps are orchestrated by the [celery director](https://ovh.github.io/celery-director/). The director itself defines the steps as celery task. Each task submits the task signature to rabbitmq to route it to the destination container. The task steps and pipeline definition are stored in `src/pipeline`. 

The director provides a web interface to start-up the pipeline and review previous executions. Additionally, there is a REST API to query and control the pipeline.

```
docker-compose up -d director
```

Afterwards, point your browser to http://localhost:8000 to access director's WebUI.

Rabbitmq records all celery task executions. You may want to review previous executions and other KPIs using [flower](https://flower.readthedocs.io/en/latest/). Flower is automatically started with the director. Point your brower to http://localhost:5555 to access flower. 


## ludwig

[ludwig](https://ludwig.ai/) is the YASMaPE's workhorse.

## mflow

[mlflow](https://mlflow.org/) supports ML model lifecycle management. It records ML experiments, i.e. their code, data, config and results. mlflow collects data and artifacts and offers a REST-enabled query possibility. 

mlflow integrates nicely with ludwig.

## Modelcards

We document the results and the ML models producing them using [verifyml's modelcards](https://www.verifyml.com/). Modelcards documents a ML model from different perspectives. By making the model's purpose and its properties explicit, modelcards enable and facilitate a responsible thinking for both, the model developer and model's user.

The modelcard sources some data from the mflow.

Check out [`create_modelcard` notebook](../notebooks/create_modelcard.ipynb).

## Gist

gists are small code snippets and other paste-style docs which are discovered during the development of YASMaPE.

See [gist.md](gist.md) for a list.
