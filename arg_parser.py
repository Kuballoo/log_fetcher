from logger import logger
import CONFIG

import argparse
from pathlib import Path

class ArgParser:
    """
    Command-line argument parser for the Log Fetcher tool.

    Provides parsing for input/output paths, log types, network address,
    compression flag, and number of threads.
    """

    def __init__(self):
        """
        Initialize the ArgParser instance and define CLI arguments.

        Logs initialization if debugging is enabled in CONFIG.
        """
        if CONFIG.DEBUG.get("arg_parser", False):
            logger.log("arg_parser", "Initialized ArgParser", level="DEBUG")
        
        self.__args = None

        self.parser = argparse.ArgumentParser(
            prog="Log Fetcher",
            description="Log Fetcher is a tool designed to fetch and process Windows logs efficiently."
        )
        self.parser.add_argument(
            "--input",
            type=str,
            default="C:/Windows/System32/winevt/Logs",
            help='Input file path, e.g. "C:/Windows/System32/winevt/Logs"'
        )
        self.parser.add_argument(
            "--output",
            type=str,
            required=True,
            help='Output file path, e.g. "C:/Users/Kowalski/logs"'
        )
        self.parser.add_argument(
            "--log-types",
            type=str,
            nargs='+',
            default=["Security", "System", "Application"],
            help="Types of logs to fetch, e.g. Security System Application"
        )
        self.parser.add_argument(
            "--ipv4-addr",
            type=str,
            default="192.168.1.0/24",
            help="Network address in CIDR notation, e.g. 192.168.1.0/24"
        )
        self.parser.add_argument(
            "--compress",
            action="store_true",
            help="Enable compression for output files"
        )
        self.parser.add_argument(
            "--threads",
            type=int,
            default=4,
            help="Number of threads to use"
        )
    
    def generate_args_dict(self):
        """
        Parse command-line arguments and return them as a dictionary.

        Normalizes input and output paths to use forward slashes.
        Logs all parsed arguments if debugging is enabled.

        Returns:
            dict: Dictionary of argument names and their values.
        """
        self.__args = self.parser.parse_args()
        
        self.__args.input = Path(self.__args.input.replace("\\", "/"))
        self.__args.output = Path(self.__args.output.replace("\\", "/"))
        
        if CONFIG.DEBUG.get("arg_parser", True):
            for key, value in vars(self.__args).items():
                logger.log("arg_parser", f"Argument: {key} = {value}", level="DEBUG")

        return vars(self.__args)
