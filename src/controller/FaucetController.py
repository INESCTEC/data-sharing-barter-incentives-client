import os
import requests

from time import sleep
from loguru import logger


class FaucetController:
    BASE_URL = os.environ["IOTA_FAUCET_URL"]

    def __init__(self):
        self.current_time = 0

    def request_tokens(self, address, max_retries=10, seconds_between_retries=60):
        n_retries = 0
        response_msg = ""
        while n_retries <= max_retries:
            # try approach for old testnet
            logger.info("Trying old address ...")
            r = requests.get(self.BASE_URL + "/api", params={'address': address})
            logger.info(r.status_code)
            if r.status_code == 404:
                logger.info("Trying new address ...")
                # approach for new testnet (if old does compute)
                r = requests.post(self.BASE_URL, json={'address': address})
                logger.info(r.status_code)

            status_code = r.status_code
            response_msg = r.text
            if status_code not in [200, 202]:
                logger.warning("Failed to request. Details:")
                logger.warning(status_code, response_msg)
                logger.warning(f"Retrying ... {n_retries}/{max_retries}")
                sleep(seconds_between_retries)
                n_retries += 1
            else:
                break
        return response_msg
