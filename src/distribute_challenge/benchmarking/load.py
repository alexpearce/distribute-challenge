"""Stress-test the Celery task queue and plot the resulting throughput.

Example run:

.. code-block:: none

    poetry run python -m distribute_challenge.benchmarking.load --min-workers 1 --max-workers 10 --runtime 30

This will launch groups of workers, load them with tasks, and monitor the
throughput over a `runtime` of 30 seconds. Worker groups will begin with 1
worker (`min-workers`), increasing by one worker at a time up to 10 workers
(`max-workers`).
"""
import argparse
import datetime
import functools
import os
import subprocess
import threading
import time

import billiard
import matplotlib.pyplot as plt

from .. import compute_this
from ..execution_backends.celery import CeleryExecutionBackend, _app
from .monitor import Monitor


def monkey_patch():
    """Monkey-patch Celery.

    This is a work-around for the AsyncResult destructor requiring a Redis
    connection, which does not exist at the end of this script. The destructor
    should be called much earlier (when the execution backend returns the
    task's result), but I suspect the issue discussed in celery/celery#6772 is
    causing the reference to hang around much longer than necessary.
    """
    from celery.result import AsyncResult

    delattr(AsyncResult, "__del__")


@compute_this
def task(runtime=1):
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    def loop():
        while True:
            fib(100)

    p = billiard.Process(target=loop)
    p.start()
    time.sleep(runtime)
    p.terminate()


def plot_throughput(data, fname):
    fig, ax = plt.subplots()
    for nworkers in data:
        xs, ys = zip(*data[nworkers])
        xs = [(x - xs[0]).total_seconds() for x in xs]
        ax.plot(xs, ys, label=f"N = {nworkers}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Throughput [tasks / second]")
    ax.set_ylim(bottom=0)
    ax.grid("--")
    ax.legend()
    fig.savefig(fname)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--min-workers", type=int, default=1, help="Starting number of workers."
    )
    parser.add_argument(
        "--max-workers", type=int, default=1, help="Ending number of workers."
    )
    parser.add_argument(
        "--runtime", type=int, default=30, help="Total stress test runtime in seconds."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose messages."
    )
    args = parser.parse_args()

    # The `docker compose` commands require the compose configuration
    if not os.path.exists("docker-compose.yaml"):
        raise Exception(
            "Docker compose configuration not found; you should run this script from the repository root"
        )

    monkey_patch()

    data = {}
    backend = CeleryExecutionBackend()
    target = functools.partial(task().compute, backend=backend)
    for nworkers in range(args.min_workers, args.max_workers + 1):
        print(f"Running nworkers={nworkers}")

        # Start the containers and wait for them to initialise
        subprocess.run(
            ["docker", "compose", "up", "--scale", f"worker={nworkers}", "--detach"],
            stdout=subprocess.DEVNULL,
        )
        # TODO is there a cleverer way of checking for initialisation?
        time.sleep(60)

        # Each task takes about a second and we want the system fully loaded
        # for `args.runtime` seconds
        ntasks = args.runtime * nworkers
        monitor = Monitor(_app, verbose=args.verbose)
        threads = [threading.Thread(target=target) for _ in range(ntasks)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Wait for the throughput measurement to cool down to zero
        time.sleep(5)
        data[nworkers] = monitor.stop()

        # Stop the containers
        subprocess.run(
            ["docker", "compose", "down"],
            stdout=subprocess.DEVNULL,
        )

    # Plot the results
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    fname = f"{now}-{args.min_workers}-to-{args.max_workers}-workers-throughput.pdf"
    plot_throughput(data, fname)
