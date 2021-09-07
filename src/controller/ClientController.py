from time import time
from loguru import logger
from http import HTTPStatus

from .helpers.Endpoint import *
from .RequestController import RequestController
from .exception.APIException import *


class ClientController(RequestController):
    seller_role_id = 2

    def __init__(self):
        RequestController.__init__(self)
        self.access_token = ""

    def __check_if_token_exists(self):
        if self.access_token is None:
            e_msg = "Access token is not yet available. Login first."
            logger.error(e_msg)
            raise ValueError(e_msg)

    def set_access_token(self, token):
        self.access_token = token

    def __request_template(self,
                           endpoint_cls: Endpoint,
                           log_msg: str,
                           exception_cls,
                           data: dict = None,
                           params: dict = None) -> dict:
        self.__check_if_token_exists()
        t0 = time()
        rsp = self.request(
            endpoint=endpoint_cls,
            data=data,
            params=params,
            auth_token=self.access_token)
        # -- Inspect response:
        if rsp.status_code == HTTPStatus.OK:
            logger.debug(f"{log_msg} ... Ok! ({time() - t0:.2f})")
            return rsp.json()
        else:
            log_msg_ = f"{log_msg} ... Failed! ({time() - t0:.2f})"
            logger.error(log_msg_ + f"\n{rsp.json()}")
            raise exception_cls(message=log_msg_, errors=rsp.json())

    def register(self, email, password, password_conf,
                 first_name, last_name, role):
        t0 = time()
        log_ = f"Registering user {email}"
        logger.debug(f"{log_} ...")
        payload = {
            "email": email,
            "password": password,
            "password_confirmation": password_conf,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
        }
        rsp = self.request(
            endpoint=Endpoint(register.POST, register.uri),
            data=payload
        )
        if rsp.status_code == HTTPStatus.OK:
            logger.debug(f"{log_} ... Ok! ({time() - t0:.2f})")
            return rsp
        else:
            log_msg = f"{log_} ... Failed! ({time() - t0:.2f})"
            logger.error(log_msg + f"\n{rsp.json()}")
            raise RegisterException(message=log_msg, errors=rsp.json())

    def login(self, email: str, password: str):
        t0 = time()
        log_ = f"Logging in user {email}"
        payload = {
            "email": email,
            "password": password
        }
        rsp = self.request(
            endpoint=Endpoint(login.POST, login.uri),
            data=payload
        )
        if rsp.status_code == HTTPStatus.OK:
            logger.debug(f"{log_} ... Ok! ({time() - t0:.2f})")
            self.access_token = rsp.json()['access']
        else:
            log_msg = f"{log_} ... Failed! ({time() - t0:.2f})"
            logger.error(log_msg + f"\n{rsp.json()}")
            raise LoginException(message=log_msg, errors=rsp.json())

    def create_wallet_withdraw_request(self, to_address: str, amount: int):
        payload = {
            "address": to_address,
            "amount": amount,
        }
        response = self.__request_template(
            endpoint_cls=Endpoint(wallet_withdraw.POST, wallet_withdraw.uri),
            log_msg=f"Withdrawing {amount} tokens to address {to_address}",
            data=payload,
            exception_cls=WalletWithdrawException
        )
        return response['data']

    def place_bid(self,
                  market_session_id: int,
                  bid_price,
                  max_payment,
                  gain_func):
        payload = {
            "market_session_id": market_session_id,
            "bid_price": bid_price,
            "max_payment": max_payment,
            "gain_func": gain_func
        }
        response = self.__request_template(
            endpoint_cls=Endpoint(market_bid.POST, market_bid.uri),
            log_msg=f"Posting bid for market session ID {market_session_id}",
            data=payload,
            exception_cls=MarketBidException
        )
        return response['data']

    def send_measurements(self, data):
        # Todo: to implement after method created valorem server.
        # Will send a JSON
        pass

    def get_forecasts(self):
        # Todo: to implement after method created valorem server.
        # Will send a JSON
        pass
