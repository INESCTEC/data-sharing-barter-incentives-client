from loguru import logger

from src.controller import WalletController, ClientController
from src.controller.exception.APIException import *


class BidException(Exception):
    pass


class ExistingBidException(Exception):
    pass


class BiddingService:
    def __init__(self):
        self.controller = ClientController()

    def list_open_session(self, user):

        logger.info("List open session ...")
        self.controller.login(user["email"], user["password"])
        try:
            response = self.controller.list_sessions()
            logger.info("Opening session ... Ok!")
        except Exception as e:
            logger.error(f"Unexpected error! {str(e)}")
            raise Exception(e)

        return response

    @staticmethod
    def get_wallet_balance(user):
        wallet_controller = WalletController(email=user["email"], password=user["password"]).connect()
        return wallet_controller.get_balance()

    def place_bid(self, user, max_payment, session_id, bid_price, resource):

        logger.info(f"Placing bid for user: {user['email']}")
        email = user["email"]
        password = user["password"]

        try:
            # -- login to market REST:
            self.controller.login(email, password)
        except LoginException:
            msg = f"Unable to login into the market platform for the user: {email}"
            logger.error(msg)
            raise BidException(msg)

        try:
            # -- Get market wallet address:
            market_wallet_address = self.controller.get_market_wallet_address()
            market_wallet_address = market_wallet_address["wallet_address"]
            # current_bids = self.controller.get_current_session_bids(session_id=session_id)
        except MarketSessionException:
            msg = "There is a problem with the market wallet address to use."
            logger.error(msg)
            raise BidException(msg)

        try:
            response = self.controller.place_bid(
                session_id=session_id,
                bid_price=bid_price,
                max_payment=max_payment,
                gain_func="mse",
                resource_id=resource
            )
            logger.info(f"Placing bid for user: {user['email']} ... Ok!")
            # -- initialize WALLET controller:
            wallet = WalletController(email=email, password=password).connect()
            node_response = wallet.transfer_tokens(amount=max_payment, address=market_wallet_address)
            logger.debug(node_response)
            logger.info(f"Transferring tokens to market wallet ... Ok!")
            tangle_msg_id = node_response['id']

        except MarketBidException as e:
            logger.error(str(e))
            raise BidException(e)

        except Exception as e:
            logger.exception(f"Unexpected error! {repr(e)}")
            raise Exception(str(e))

        response['data']['tangle_msg_id'] = tangle_msg_id
        return response['data']

    def patch_bid(self, user, bid):
        self.controller.login(user["email"], user["password"])
        return self.controller.patch_bid(bid_id=bid["id"], tangle_msg_id=bid["tangle_msg_id"])