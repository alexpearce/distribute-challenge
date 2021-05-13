Distribute challenge
====================

`distribute_challenge` is a Python package that let's you run your function
over a remote cluster. It is an implementation of [Neuro's][neuro] [distribute
challenge][challenge].

```python
>>> from distribute_challenge import compute_this
>>> @compute_this()
... def func(x):
...     return x*x
...
>>> func(2).compute()
4
```

The `compute` call pushes the function and arguments on to a job queue which is
monitored by the workers in the cluster. The first available worker pops jobs
off the queue and the result is returned to the original caller.

[![Tests](https://github.com/alexpearce/distribute-challenge/actions/workflows/tests.yml/badge.svg)](https://github.com/alexpearce/distribute-challenge/actions/workflows/tests.yml)

## Features

- Execution backend choices. Defaults to Celery to distribute work, but can be
  extended to support multiprocessing on the same machine.
- User friendly. Validates that distributed function is compatible with the
  arguments that will be passed to it, avoiding costly round-trips which would
  anyhow fail.

**Note**: because this library serialises arbitrary Python callables it should
only be used when you can trust the client.

## How it works

1. Python functions are serialised using [`cloudpickle`][cloudpickle].
2. Serialised functions and their arguments are passed to an execution backend.

The local backend just executes the function directly within the client
process.

The [Celery][celery] backend is more interesting:

1. Serialised functions and their arguments are pushed on to a task queue
   (configured to be a [Redis][redis] instance by default).
2. Celery workers pop tasks off the queue and run them.
3. Workers push function results back to the original caller via a result
   backend (also Redis by default).

[neuro]: https://www.getneuro.ai/
[challenge]: https://github.com/neuro-ai-dev/distribute-challenge
[cloudpickle]: https://github.com/cloudpipe/cloudpickle
[celery]: https://docs.celeryproject.org/en/stable/index.html
[redis]: https://redis.io/
