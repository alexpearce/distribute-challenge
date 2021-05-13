import cloudpickle

from distribute_challenge.execution_backends.local import LocalExecutionBackend


def test_local_backend():
    """The local backend should execute the function."""
    func = cloudpickle.dumps(lambda x: x * x)
    backend = LocalExecutionBackend()
    assert backend.run(func, [2], {}) == 4
