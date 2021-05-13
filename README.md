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

[neuro]: https://www.getneuro.ai/
[challenge]: https://github.com/neuro-ai-dev/distribute-challenge
