import CONFIG
from logger import logger

import ipaddress


class AddressesGenerator():
    def  __init__(self):
        if CONFIG.DEBUG.get("address_generator", True):
            logger.log("address_generator", "Initialized AddressesGenerator", level="DEBUG")
