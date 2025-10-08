import CONFIG
from logger import logger
from threads_worker import ThreadsWorker

import ipaddress, subprocess
from queue import Queue

class AddressesGenerator:
    """
    Generates network addresses from a given IPv4 network or address
    and identifies the operating system of hosts based on TTL values.
    
    Attributes:
        __ipv4_addr (str): Input IPv4 address or network in CIDR format.
        __network (IPv4Network): Parsed IP network object.
        __hosts (list): List of host addresses in the network.
        hosts_os (dict): Mapping of host IPs to identified OS types.
    """

    def __init__(self, ipv4_addr):
        """
        Initialize the AddressesGenerator instance.

        Parses the input network, generates host addresses, 
        and initializes OS mapping. Logs initialization if debugging is enabled.

        Args:
            ipv4_addr (str): IPv4 address or network in CIDR notation.
        """
        if CONFIG.DEBUG.get("address_generator", True):
            logger.log("address_generator", "Initialized AddressesGenerator", level="DEBUG")
            logger.log("address_generator", f"IPv4 Address: {ipv4_addr}", level="DEBUG")

        self.__ipv4_addr = ipv4_addr
        self.__network = None
        self.__hosts = None

        # Generate host addresses from the provided network
        self.__generate_addresses()

        # Initialize dictionary mapping host -> OS type
        self.hosts_os = {ip: "" for ip in self.__hosts}

    def __generate_addresses(self):
        """
        Generate host addresses from the provided IPv4 network input.

        Converts input to IPv4Network object and generates a list of hosts.
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
        Identify the operating system based on the TTL value.

        Args:
            ttl (int): TTL value retrieved from a network response.

        Returns:
            str: Detected OS type:
                - "Windows" if TTL is typical for Windows,
                - "Another" for other OS types,
                - "Offline" if TTL is 0 or unrecognized.
        """
        if 120 < ttl < 140:
            return "Windows"
        elif ttl == 0:
            return "Offline"
        else:
            return "Another"

    def run_task(self, host):
        """
        Check TTL for a single host and determine its OS.

        Executes a PowerShell Test-Connection command to retrieve TTL.
        Updates the hosts_os mapping. Logs responses and errors if debugging is enabled.

        Args:
            host (str): Target host IP address.
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
                logger.log("address_generator", f"{str(host)} TTL response: {ttl}", level="DEBUG")
        except UnicodeEncodeError:
            # Ignore encoding issues
            pass
        except Exception as e:
            if CONFIG.DEBUG.get("address_generator", True):
                logger.log("address_generator", f"Error occurred {e}", level="ERROR")
        
        try:
            ttl = int(ttl)
        except ValueError:
            ttl = 0

        self.hosts_os[host] = self.identify_os(ttl)

    def __run_threads(self, num_threads):
        """
        Run multiple worker threads to process hosts concurrently.

        - Populates a Queue with hosts to check.
        - Spawns `num_threads` ThreadsWorker instances.
        - Each worker executes `run_task` on hosts from the queue.
        - Waits for all threads to finish processing.

        Args:
            num_threads (int): Number of worker threads to spawn.
        """
        q = Queue()
        for host in self.__hosts:
            q.put(host)

        threads = [ThreadsWorker(q, self) for _ in range(num_threads)]
        for t in threads:
            t.start()
        q.join()

    def run_generator(self):
        """
        Main entry point to identify Windows hosts in the network.

        Runs multithreaded scanning using configured thread count.

        Returns:
            list: List of host IPs identified as running Windows.
        """
        self.__run_threads(CONFIG.THREADS_COUNT)
        return [key for key, value in self.hosts_os.items() if value == "Windows"]
