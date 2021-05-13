"""Execution backends define function runtimes.

There are two choices that ship with `distribute_challenge`:

* `local.LocalExecutionBackend`.
* `celery.CeleryExecutionBackend`.

The function `default_backend` provides a default if no backend is specified
when distributed function computed is requested.

Backend API
-----------

A backend `Backend` must provide the following API::

    instance = Backend())
    instance.run(func, args, kwargs)

where `func` is a function serialised by ``cloudpickle.dumps`` and ``args`` and
``kwargs`` are positional and keyword arguments, respectively, to be passed to
the deserialised function.
"""
from .local import LocalExecutionBackend

__all__ = ["default_backend"]


def default_backend():
    return LocalExecutionBackend()
