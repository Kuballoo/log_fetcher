import CONFIG
from logger import logger
from threads_worker import ThreadsWorker

import ipaddress, subprocess
from queue import Queue

class AddressesGenerator:
    """
    Generates network addresses from a given IPv4 address and identifies OS by TTL.

    Attributes:
        __ipv4_addr (str): The input IPv4 address or network.
        __network (IPv4Network): The parsed IP network object.
        __hosts (iterator): Iterator over the host addresses in the network.
    """

    def __init__(self, ipv4_addr):
        """
        Initialize the AddressesGenerator instance.

        Logs the initialization if debugging is enabled.

        Args:
            ipv4_addr (str): IPv4 address or network in CIDR format.
        """
        if CONFIG.DEBUG.get("address_generator", True):
            logger.log("address_generator", "Initialized AddressesGenerator", level="DEBUG")
            logger.log("address_generator", f"IPv4 Address: {ipv4_addr}", level="DEBUG")

        self.__ipv4_addr = ipv4_addr
        self.__network = None
        self.__hosts = None
        self.__generate_addresses()
        self.hosts_os = {ip: "" for ip in self.__hosts}


    def __generate_addresses(self):
        """
        Generate network and host addresses from the provided IPv4 input.

        Logs progress and errors if debugging is enabled.
        """
        if CONFIG.DEBUG.get("address_generator", True):
            logger.log("address_generator", "Generating addresses...", level="DEBUG")

        try:
            self.__network = ipaddress.ip_network(self.__ipv4_addr)
            self.__hosts = list(self.__network.hosts())
        except Exception as e:
            if CONFIG.DEBUG.get("address_generator", True):
                logger.log("address_generator", f"Error occurred {e}", level="ERROR")

    def identify_os(self, ttl):
        """
        Identify the operating system based on TTL value.

        Args:
            ttl (int): Time-to-Live value from a network response.

        Returns:
            str: OS type ("Windows", "Another", or "Offline" if unknown/offline).
        """
        if ttl > 120 and ttl < 140:
            return "Windows"
        elif ttl == 0:
            return "Offline"
        else:
            return "Another"

    def run_task(self, host):
        """
        Run a TTL check on a host to determine the OS.

        Executes a PowerShell Test-Connection command to retrieve TTL.
        Logs the response or any errors if debugging is enabled.

        Args:
            host (str): Host IP address to check.

        Returns:
            str: Identified OS type based on TTL.
        """ 
        ps = [
            "powershell",
            "-Command",
            f"(Test-Connection {str(host)} -Count 1).ResponseTimeToLive"
        ]
        ttl = ""
        try:
            result = subprocess.run(ps, capture_output=True, text=True, check=True)
            ttl = result.stdout.strip()
            if CONFIG.DEBUG.get("address_generator", True):
                logger.log("address_generator", f"{str(host)} response time: {ttl}", level="DEBUG")           
        except UnicodeEncodeError:
            pass
        except Exception as e:
            if CONFIG.DEBUG.get("address_generator", True):
                logger.log("address_generator", f"Error occurred {e}", level="ERROR")
        
        try:
            ttl = int(ttl)
        except ValueError:
            ttl = 0
        self.hosts_os[host] = self.identify_os(ttl)

    def run_threads(self, num_threads=4):
        """
        Run multiple worker threads to process all hosts concurrently.

        - Creates a Queue with all hosts to be checked.
        - Spawns `num_threads` ThreadsWorker instances, each of which
        calls this object's `run_task(host)` for items in the queue.
        - Starts all threads and waits for them to finish with join().
        
        Args:
            num_threads (int, optional): Number of worker threads to run. Defaults to 4.
        """
        q = Queue()
        for host in self.__hosts:
            q.put(host)

        threads = [ThreadsWorker(q, self) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()


