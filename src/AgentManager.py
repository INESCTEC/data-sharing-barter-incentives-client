import os
import json

from loguru import logger

from src.util.mock.user_generators import generate_users
from src.controller import FaucetController, WalletController, ClientController


class AgentManager:
    USERS_FILE_DIR = os.environ["USERS_FILE_DIR"]

    def __init__(self):
        self.faucet = FaucetController()
        self.wallet_user_list = []
        os.makedirs(self.USERS_FILE_DIR, exist_ok=True)
        self.users_file = os.path.join(self.USERS_FILE_DIR,
                                       "users.json")

    def load_available_users(self):
        # Load users from JSON file:
        with open(self.users_file, 'r') as outfile:
            self.wallet_user_list = json.load(outfile)
        return self.wallet_user_list

    def create_user_wallets(self, nr_users):
        user_list = generate_users(nr_users=nr_users)
        wallet_user_list = []
        for user in user_list:
            email = user["email"]
            password = user["password"]
            logger.info(f'Creating new wallet: {email}')
            try:
                # Create wallet & account:
                wallet = WalletController(email=email, password=password)
                wallet.create_wallet(store_mnemonic=True)
                wallet.create_account(alias=email)
                # Get address & request tokens from faucet:
                address = wallet.get_address()["address"]["inner"]
                self.faucet.request_tokens(address=address)
                # Save:
                user["wallet_address"] = address
                wallet_user_list.append(user)
                logger.info(f'Creating new wallet: {email} ... Ok!')
            except Exception:
                logger.exception(f'Creating new wallet: {email} ... Failed!')

        with open(self.users_file, 'w') as outfile:
            json.dump(wallet_user_list, outfile, indent="\t")

        self.wallet_user_list = wallet_user_list
        return self.wallet_user_list

    def get_wallet_balances(self):
        for user in self.wallet_user_list:
            email = user["email"]
            password = user["password"]
            try:
                # Create wallet & account:
                wallet = WalletController(email=email,
                                          password=password).connect()
                balance = wallet.get_balance()
                logger.info(f'User {email} balance is {balance}')
            except Exception:
                logger.exception(
                    f'Failed to retrieve balance for user {email}!')
        return

    def get_wallet_addresses(self):
        for user in self.wallet_user_list:
            email = user["email"]
            password = user["password"]
            try:
                # Create wallet & account:
                wallet = WalletController(email=email,
                                          password=password).connect()
                address = wallet.get_address()["address"]["inner"]
                logger.info(f'User {email} address is {address}')
            except Exception:
                logger.exception(
                    f'Failed to retrieve address for user {email}!')
        return

    def request_tokens(self):
        for user in self.wallet_user_list:
            email = user["email"]
            password = user["password"]
            logger.info(f'Requesting tokens for user: {email}')
            try:
                # Create wallet & account:
                wallet = WalletController(email=email,
                                          password=password).connect()
                # Get address & request tokens from faucet:
                address = wallet.get_address()["address"]["inner"]
                self.faucet.request_tokens(address=address)
                logger.info(f'Requesting tokens for user: {email} ... Ok!')
            except Exception:
                logger.exception(f'Failed to request tokens for user {email}!')

    def register_users(self):
        # Initialize API controller:
        controller = ClientController()
        registered_users = []
        for user in self.wallet_user_list:
            logger.info(f"Registering user: {user['email']}")
            try:
                # Register user:
                controller.register(
                    email=user["email"],
                    password=user["password"],
                    password_conf=user["password"],
                    first_name=user["first_name"],
                    last_name=user["last_name"],
                    role=user["role"],
                )
                controller.login(
                    email=user["email"],
                    password=user["password"]
                )
                controller.register_wallet_address(user["wallet_address"])
                registered_users.append(user)
                logger.info(f"Registering user: {user['email']} ... Ok!")
            except Exception:
                logger.exception(
                    f"Registering user: {user['email']} ... Failed!")

        return registered_users

    def place_bids(self, max_payment, bid_price):
        # Initialize API controller:
        controller = ClientController()

        for user in self.wallet_user_list:
            logger.info(f"Placing bid for user: {user['email']}")
            email = user["email"]
            password = user["password"]
            try:
                # -- login to market REST:
                controller.login(user['email'], user['password'])
                # -- Get market wallet address:
                market_wallet_address = controller.get_market_wallet_address()
                # -- Get current last active session (status='closed'):
                session_data = controller.list_last_session(status='open')
                # Get session_id & fetch data for that session:
                active_session_id = session_data["market_session_id"]
                # --------------
                # -- initialize WALLET controller:
                wallet = WalletController(email=email,
                                          password=password).connect()
                node_response = wallet.transfer_tokens(
                    amount=max_payment,
                    address=market_wallet_address
                )
                tangle_msg_id = node_response['id']
                # -- Place bid & IOTAs transaction confirmation:
                response = controller.place_bid(
                    session_id=active_session_id,
                    bid_price=bid_price,
                    max_payment=max_payment,
                    gain_func="mse",
                    tangle_msg_id=tangle_msg_id
                )
                logger.info(response)
                logger.info(f"Placing bid for user: {user['email']} ... Ok!")
            except Exception:
                logger.exception(f"Placing bid for user: {user['email']} "
                                 f"... Failed!")
        return

    def transfer_balance_to_address(self, address):
        for user in self.wallet_user_list:
            logger.info(
                f"Transferring user {user['email']} balance to firefly")
            email = user["email"]
            password = user["password"]
            try:
                # -- initialize WALLET controller:
                wallet = WalletController(email=email,
                                          password=password).connect()
                balance = wallet.get_balance()["available"]
                node_response = wallet.transfer_tokens(
                    amount=balance,
                    address=address
                )
                logger.info(node_response)
            except Exception:
                logger.exception(f"Placing bid for user: {user['email']} "
                                 f"... Failed!")
        return
