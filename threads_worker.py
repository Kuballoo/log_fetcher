from threading import Thread
from queue import Queue

class ThreadsWorker(Thread):
    """
    Base class for creating worker threads that process items from a queue.

    Subclasses should implement the `run_task` method to define the work.
    """

    def __init__(self, task_queue, *args, **kwargs):
        """
        Initialize the ThreadsWorker instance.

        Args:
            task_queue (Queue): Queue containing items to process.
            *args, **kwargs: Additional arguments passed to Thread constructor.
        """
        super().__init__(*args, **kwargs)
        self.task_queue = task_queue

    def run_task(self, item):
        """
        Placeholder for processing a single item.

        Must be implemented in subclasses.

        Args:
            item: Item from the queue to process.

        Raises:
            Exception: Always, since this method must be overridden.
        """
        raise Exception("You have to implement run_task method!")
    
    def run(self):
        """
        Continuously process items from the queue until it is empty.

        Calls `run_task` for each item and marks it as done.
        """
        while not self.task_queue.empty():
            item = self.task_queue.get()
            try:
                self.run_task(item)
            finally:
                self.task_queue.task_done()

    @classmethod
    def run_threads(cls, items, num_threads=4):
        """
        Start multiple threads to process a list of items concurrently.

        Args:
            items (list): Items to process.
            num_threads (int, optional): Number of worker threads. Defaults to 4.
        """
        q = Queue()
        for item in items:
            q.put(item)

        threads = [cls(q) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
