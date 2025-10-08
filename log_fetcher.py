import CONFIG
from logger import logger
from threads_worker import ThreadsWorker

import ipaddress, subprocess
from queue import Queue
from pathlib import Path, PureWindowsPath

class LogFetcher:
    """
    Class responsible for fetching Windows log files from remote hosts.

    Supports multithreaded fetching, logging of operations, and error handling.
    """

    def __init__(self, ips, input_path, output_path, log_types):
        """
        Initialize the LogFetcher instance.

        Args:
            ips (list): List of target host IPs or hostnames.
            input_path (str/Path): Source path of log files on remote hosts.
            output_path (str/Path): Destination path for storing fetched logs.
            log_types (list): List of log types to fetch, e.g. ["Security", "System"].

        Logs initialization if debugging is enabled in CONFIG.
        """
        if CONFIG.DEBUG.get("log_fetcher", True):
            logger.log("log_fetcher", "Initialized LogFetcher", level="DEBUG")

        self.__ips = ips
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.log_types = log_types

    def run_task(self, host):
        """
        Fetch logs from a single host.

        Constructs network path to remote host, iterates over log types,
        and copies each log file using PowerShell.

        Args:
            host (str): Target host IP or hostname.
        """
        drive = self.input_path.drive.rstrip(":")
        path_to_user = PureWindowsPath(f"\\\\{host}\\{drive}$") / self.input_path.relative_to(self.input_path.anchor)
        
        for t in self.log_types:
            dest_folder = self.output_path / t  # Destination folder for this log type
            
            src = path_to_user / (t + ".evtx")  # Full source path on remote host
            dest = dest_folder / f"{t}_{host}.evtx"  # Destination file with host appended
            
            ps = [
                "powershell",
                "-Command",
                f'Copy-Item "{src}" "{dest}"'  # PowerShell copy command
            ]
            
            try:
                subprocess.run(ps, check=True)  # Execute copy command
            except Exception as e:
                if CONFIG.DEBUG.get("log_fetcher", True):
                    logger.log("log_fetcher", f"Error occurred {e}", level="ERROR")

    def __run_threads(self, num_threads):
        """
        Run multiple threads to fetch logs from all hosts concurrently.

        Uses a queue to manage hosts and ThreadsWorker to perform tasks.

        Args:
            num_threads (int): Number of worker threads to spawn.
        """
        q = Queue()

        # Add all target hosts to the queue
        for ip in self.__ips:
            q.put(ip)
        
        # Create and start worker threads
        threads = [ThreadsWorker(q, self) for _ in range(num_threads)]
        for t in threads:
            t.start()
        
        # Wait until all tasks in the queue are processed
        q.join()

    def run_fetcher(self):
        """
        Main entry point to fetch logs from all hosts.

        Ensures destination folders exist for each log type and
        triggers multithreaded fetching using configured thread count.
        """
        # Ensure destination folders exist
        for t in self.log_types:
            dest_dir = self.output_path / t
            dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Run threads to fetch logs
        self.__run_threads(CONFIG.THREADS_COUNT)
