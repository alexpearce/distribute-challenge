"""An execution backend which runs the function on the client machine."""
import cloudpickle


class LocalExecutionBackend:
    """Executes a function locally within the client process."""

    def run(self, serialised_func, args, kwargs):
        func = cloudpickle.loads(serialised_func)
        return func(*args, **kwargs)
