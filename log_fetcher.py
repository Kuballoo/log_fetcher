import CONFIG
from logger import logger
from threads_worker import ThreadsWorker

import subprocess
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
        path_to_user = PureWindowsPath(f"\\\\{str(host)}\\{drive}$") / self.input_path.relative_to(self.input_path.anchor)
        
        for t in self.log_types:
            dest_folder = self.output_path / t 
            
            src = path_to_user / (t + ".evtx")
            dest = dest_folder / f"{t}_{str(host)}.evtx"
            
            ps = [
                "powershell",
                "-Command",
                f'Copy-Item "{src}" "{dest}"'
            ]
            
            try:
                subprocess.run(ps, check=True)
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

        for ip in self.__ips:
            q.put(ip)
        
        threads = [ThreadsWorker(q, self) for _ in range(num_threads)]
        for t in threads:
            t.start()
        
        q.join()

    def run_fetcher(self):
        """
        Main entry point to fetch logs from all hosts.

        Ensures destination folders exist for each log type and
        triggers multithreaded fetching using configured thread count.
        """
        for t in self.log_types:
            dest_dir = self.output_path / t
            dest_dir.mkdir(parents=True, exist_ok=True)
        
        self.__run_threads(CONFIG.THREADS_COUNT)
