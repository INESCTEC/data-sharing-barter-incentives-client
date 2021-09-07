import os
import requests

from time import sleep


class FaucetController:
    BASE_URL = os.environ["FAUCET_URL"]

    def __init__(self):
        self.current_time = 0

    def request_tokens(self, address, max_retries=10, seconds_between_retries=60):
        n_retries = 0
        response_msg = ""
        while n_retries <= max_retries:
            r = requests.get(self.BASE_URL + "/api", params={'address': address})
            status_code = r.status_code
            response_msg = r.text
            if status_code != 200:
                print("Failed to request. Details:")
                print(status_code, response_msg)
                print(f"Retrying ... {n_retries}/{max_retries}")
                sleep(seconds_between_retries)
                n_retries += 1
            else:
                break
        return response_msg
