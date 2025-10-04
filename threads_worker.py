from threading import Thread
from queue import Queue

class ThreadsWorker(Thread):
    """
    Worker thread that processes items from a queue using a provided worker object.

    The worker object must implement a `run_task(item)` method.
    """

    def __init__(self, task_queue: Queue, worker_obj, *args, **kwargs):
        """
        Initialize the thread.

        Args:
            task_queue (Queue): Queue of items to process.
            worker_obj: Object with a `run_task(item)` method.
            *args, **kwargs: Additional arguments for Thread constructor.
        """
        super().__init__(*args, **kwargs)
        self.task_queue = task_queue
        self.worker_obj = worker_obj

    def run(self):
        """
        Process items from the queue until it is empty.

        For each item, calls `worker_obj.run_task(item)`.
        """
        while not self.task_queue.empty():
            item = self.task_queue.get()
            try:
                self.worker_obj.run_task(item)
            finally:
                self.task_queue.task_done()
