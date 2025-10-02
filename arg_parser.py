from logger import logger
import CONFIG

import argparse
from pathlib import Path

class ArgParser():
    def __init__(self):
        if CONFIG.DEBUG.get("arg_parser", False):
            logger.log("arg_parser", "Initialized ArgParser", level="DEBUG")
        
        self.__args = None

        self.parser = argparse.ArgumentParser(
            prog="Log Fetcher",
            description="Log Fetcher is tool designed to fetch and process windows logs efficiently."
                                              )
        self.parser.add_argument("--input", type=str, default="C:/Windows/System32/winevt/Logs", help="Input file path, ex. \"C:/Windows/System32/winevt/Logs")
        self.parser.add_argument("--output", type=str, required=True, help="Output file path, ex. \"C:/Users/Kowalski/logs")
        self.parser.add_argument("--log-types", type=str, nargs='+', default=["Security", "System", "Application"], help="Types of logs to fetch, e.g. Security System Application")
        self.parser.add_argument("--compress", action="store_true", help="Enable compression for output files")
        self.parser.add_argument("--threads", type=int, default=4, help="Number of threads to use")
    
    def generate_args_dict(self):
        self.__args = self.parser.parse_args()
        
        self.__args.input = Path(self.__args.input.replace("\\", "/"))
        self.__args.output = Path(self.__args.output.replace("\\", "/"))
        
        if CONFIG.DEBUG.get("arg_parser", True):
            for key, value in vars(self.__args).items():
                logger.log("arg_parser", f"Argument: {key} = {value}", level="DEBUG")

        return vars(self.__args)
