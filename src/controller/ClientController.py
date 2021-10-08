from time import time
from loguru import logger
from http import HTTPStatus

from src.controller.helpers.Endpoint import *
from src.controller.RequestController import RequestController
from src.controller.exception.APIException import *


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

    def register_wallet_address(self, address):
        payload = {
            "wallet_address": address,
        }
        response = self.__request_template(
            endpoint_cls=Endpoint(wallet_address.POST, wallet_address.uri),
            log_msg=f"Registering wallet address: {address}",
            data=payload,
            exception_cls=MarketAccountException
        )
        return response['data']

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

    def get_market_wallet_address(self):
        response = self.__request_template(
            endpoint_cls=Endpoint(market_wallet_address.GET,
                                  market_wallet_address.uri),
            log_msg=f"Getting market wallet address",
            exception_cls=MarketSessionException
        )
        return response['data']

    def get_market_balance(self):
        response = self.__request_template(
            endpoint_cls=Endpoint(market_balance.GET,
                                  market_balance.uri),
            log_msg=f"Getting market account balance",
            exception_cls=MarketSessionException
        )
        return response['data']

    def list_last_session(self, status: str):
        params = {"status": status}
        response = self.__request_template(
            endpoint_cls=Endpoint(market_session.GET, market_session.uri),
            log_msg=f"Getting last '{status}' market session",
            params=params,
            exception_cls=MarketSessionException
        )
        # Get sessions data - check if there are open sessions:
        sessions = response['data']
        if len(sessions) > 0:
            sessions = sessions[-1]
            return sessions
        elif len(sessions) == 0:
            log_msg = f"No market sessions with the status: {status}"
            logger.warning(log_msg)
            raise NoMarketSessionException(message=log_msg,
                                           errors=response)

    def place_bid(self,
                  session_id: int,
                  bid_price,
                  max_payment,
                  gain_func,
                  tangle_msg_id):

        # Todo: to implement after method created valorem server.
        # Will send a JSON
        # Should place a bid considering an add provided by valorem
        # (build other method to get that address)
        payload = {
            "market_session": session_id,
            "bid_price": bid_price,
            "max_payment": max_payment,
            "gain_func": gain_func,
            "tangle_msg_id": tangle_msg_id
        }
        response = self.__request_template(
            endpoint_cls=Endpoint(market_bid.POST, market_bid.uri),
            log_msg=f"Posting bid for market session ID: {session_id}",
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
