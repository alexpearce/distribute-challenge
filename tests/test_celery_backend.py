import cloudpickle
import pytest

from distribute_challenge.execution_backends.celery import CeleryExecutionBackend


@pytest.mark.celery
def test_celery_backend():
    """The Celery backend should execute the function."""
    func = cloudpickle.dumps(lambda x: x * x)
    backend = CeleryExecutionBackend()
    assert backend.run(func, [2], {}) == 4


def test_celery_backend_local():
    """The Celery backend should allow for local execution.

    Unlike the default Celery behaviour, where the ``_run_function`` task is
    executed in a separate worker process, this test runs the task in the same
    process as all other tests. This allows the coverage report to see
    ``_run_function`` being hit.
    """
    func = cloudpickle.dumps(lambda x: x * x)
    backend = CeleryExecutionBackend(local=True)
    assert backend.run(func, [3], {}) == 9
