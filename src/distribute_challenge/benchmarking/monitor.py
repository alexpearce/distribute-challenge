"""A real-time Celery worker throughput monitor."""
import datetime
import threading
import time

import celery


class Monitor:
    def __init__(self, app, verbose=False):
        """Instantiation and start a real-time throughput monitor.

        Initialisation immediately starts two worker threads:

        1. A Celery events receiver which tracks the number of completed tasks.
        2. Periodic computation of the throughput given time alive and the
        number of completed tasks.

        The computation measures the average throughput using an exponential
        moving average. This reduces the effect of historical throughput
        values, giving a more accurate representation of the instantaneous
        throughput.

        The monitoring  stopped explicitly by calling `stop()`, which closes
        the child threads.
        """
        self.app = app
        self.state = app.events.State()
        self.start_time = datetime.datetime.now()
        self.ncompleted = 0
        self.throughput = 0
        # Exponential smoothing factor
        self.alpha = 0.75
        # Lock to acquire before modifying members in a thread
        self.lock = threading.Lock()
        self.verbose = verbose

        # Start the Celery real-time monitor thread
        self.run_thread = threading.Thread(target=self.run)
        self.run_thread.start()

        # Start the throughput monitoring thread
        self.should_stop = False
        self.monitor_thread = threading.Thread(target=self.monitor)
        self.monitor_thread.start()

    def run(self):
        with self.app.connection() as connection:
            self.recv = self.app.events.Receiver(
                connection,
                handlers={
                    "task-succeeded": self.task_completed,
                },
            )
            self.recv.capture()

    def task_completed(self, event):
        """Register a completed task."""
        with self.lock:
            self.ncompleted += 1

    def monitor(self):
        """Continously monitor task throughput."""
        self.data = []
        while not self.should_stop:
            now = datetime.datetime.now()
            with self.lock:
                delta = now - self.start_time
                t1 = self.ncompleted / (delta.seconds or 1)
                self.throughput = self.alpha * t1 + (1 - self.alpha) * self.throughput
                self.ncompleted = 0
                self.start_time = now
            if self.verbose:
                print(f"Throughput: {self.throughput:.2f} tasks / second")
            self.data.append((now, self.throughput))
            time.sleep(1)

    def stop(self):
        self.should_stop = self.recv.should_stop = True
        self.monitor_thread.join()
        self.run_thread.join()
        return self.data
