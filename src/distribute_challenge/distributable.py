"""Helpers for creating distributable functions."""
import functools
import inspect


class Distributable:
    def __init__(self, func, args, kwargs):
        """Return an wrapped `func` that can be computed remotely.

        This implementation assumes `args` and `kwargs` suitable match the
        signature of `func` such that `func(*args, **kwargs)` is valid.

        Example:

            >>> d = Distributable(lambda x: x *  x, (2,), {})
            >>> d.compute()
            4

        Args:
            func (callable): Function whose execution will be distributed.
            args (tuple): Positional arguments to be passed to `func`.
            kwargs (dict): Keyword arguments to be passed to `func`.
        """
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def compute(self):
        """Return the evaluatation of the function."""
        return self._func(*self._args, **self._kwargs)


def compute_this(func=None):
    """Return a wrapped `func` whose computation can be distributed.

    Rather than being executed immediately the wrapped function returns a
    `Distributable` object when called.

    Examples:

        >>> @compute_this
        ... def square(x):
        ...     return x * x
        ...
        >>> square(2)
        <distribute_challenge.distributable.Distributable object at 0x...>

    Args:
        func (callable): Function to be distributed.

    Raises:
        TypeError: If the wrapped function is called with arguments that are
        incompatible with the function's signature. For example:

            >>> compute_this(lambda x: x * x)(1, 2)
            Traceback (most recent call last):
                ...
            TypeError: too many positional arguments
    """
    # Decorated with parenthesis
    # We support this API in case we want to add optional arguments to the
    # decorator in the future, e.g. `@compute_this(backend="local")`
    if func is None:
        return functools.partial(compute_this)

    # Decorated without parenthesis
    signature = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Verify that the function's signature is compatible with the arguments
        signature.bind(*args, **kwargs)
        return Distributable(func, args, kwargs)

    return wrapper
