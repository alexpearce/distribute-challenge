import inspect

import pytest

from distribute_challenge import Distributable, compute_this
from distribute_challenge.execution_backends.local import LocalExecutionBackend


def test_decoration_callable():
    """The decorator should return a callable with or without parenthesis."""

    @compute_this
    def f():
        """Test docstring."""
        pass

    @compute_this()
    def g():
        pass

    assert callable(g)


def decoration_preserves_details():
    """The decorator should preserve function docstring and signature."""

    def f(x, flag=False):
        """Test docstring."""
        pass

    wrapped = compute_this()
    assert inspect.signature(wrapped) == inspect.signature(f)
    assert wrapped.__doc__ == f.__doc__


def test_decoration_call():
    """The decorated function should return Distributable when called."""

    @compute_this
    def f(x):
        return x * x

    prepared = f(2)
    assert isinstance(prepared, Distributable)
    assert prepared._args == (2,)
    assert not prepared._kwargs


def test_decoration_computation():
    """The decorated function can be computed after binding arguments."""
    wrapped = compute_this(lambda x: x * x)
    assert wrapped(2).compute() == 4
    # Wrapped function be called again
    assert wrapped(3).compute() == 9


def test_no_arguments_computation():
    """Wrapped function must be called before `compute`."""
    wrapped = compute_this(lambda x: x * x)
    with pytest.raises(AttributeError):
        wrapped.compute()


def test_signature_checking():
    """The wrapped function should verify arguments match the function signature."""
    wrapped = compute_this(lambda x: x * x)
    # No error, arguments are correct
    wrapped(2)
    # Error, arguments don't match the wrapped function's signature
    with pytest.raises(TypeError):
        wrapped()


def test_computation():
    """Distributable.compute should return the function evaluation result."""
    d = Distributable(lambda x: x * x, [2], {})
    assert d.compute() == 4
    # Can compute multiple times
    assert d.compute() == 4


def test_custom_backend():
    """Distributable.compute should accept a custom backend instance."""

    class TestBackend:
        def __init__(self):
            self.executed = False

        def run(self, *args):
            self.executed = True

    backend = TestBackend()
    assert not backend.executed
    d = Distributable(lambda: 0, [], {})
    d.compute(backend=backend)
    assert backend.executed
