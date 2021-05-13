"""An execution backend which pushes the function to a Celery task queue."""
import os

import celery
import cloudpickle


class CeleryConfig:
    """Default Celery configuration.

    Some parameters can be overriden by environment variables:

    .. list-table::
        :header-rows: 1

        * - Parameter
          - Environment variable
        * - ``broker_url``
          - ``CELERY_BROKER_URL``
        * - ``result_backend``
          - ``CELERY_RESULT_BACKEND``
    """

    accept_content = {"application/x-python-serialize"}
    broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost//")
    result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis")
    event_serializer = "pickle"
    task_serializer = "pickle"
    result_serializer = "pickle"
    default_task_queue = "tasks"


_app = celery.Celery(CeleryConfig.default_task_queue, config_source=CeleryConfig)


@_app.task
def _run_function(serialised_func, args, kwargs):
    func = cloudpickle.loads(serialised_func)
    return func(*args, **kwargs)


class CeleryExecutionBackend:
    """Pushes a function to a Celery task queue and awaits the result."""

    def __init__(self, local=False):
        self._local = local

    def run(self, serialised_func, args, kwargs):
        task = _run_function.apply if self._local else _run_function.apply_async
        task_args = (serialised_func, args, kwargs)
        return task(args=task_args).get()
