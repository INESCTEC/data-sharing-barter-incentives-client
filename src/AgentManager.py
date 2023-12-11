import os
import json
import datetime as dt
from app.schemas import UserRegistrationSchema, MeasurementsSchema
import pandas as pd
from loguru import logger

from src.controller import FaucetController, WalletController, ClientController
from src.controller.exception.APIException import *


class AgentManager:
    USERS_FILE_DIR = os.environ["USERS_FILE_DIR"]

    def __init__(self):
        self.controller = ClientController()
        self.faucet = FaucetController()

        os.makedirs(self.USERS_FILE_DIR, exist_ok=True)
        self.users_file = os.path.join(self.USERS_FILE_DIR, "users.json")

        # Check if users.json exists, if not, create it
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump([], f)
                self.wallet_user_list = []
        else:
            self.wallet_user_list = self.load_available_users()

    def save_data_to_file(self, data):
        with open(self.users_file, 'w') as outfile:
            json.dump(data, outfile, indent="\t")

    def login(self, user):
        try:
            self.controller.login(user['email'], user['password'])
        except LoginException as e:
            raise Exception(e)

    def get_wallet_user_list(self):
        return self.wallet_user_list

    def get_user_by_email(self, email):
        self.load_available_users()
        for user in self.wallet_user_list:
            if user['email'] == email:
                return user
        return None

    def register_wallet(self, user, address):

        try:
            response = self.controller.register_wallet_address(address)
            for user in self.wallet_user_list:
                if user['email'] == user['email']:
                    user['registered_wallet'] = True
        except RegisterWalletException as e:
            raise RegisterWalletException(message=str(e), errors=str(e))

        # update my file
        self.save_data_to_file(self.wallet_user_list)
        return response

    def load_available_users(self):
        # Load users from JSON file:
        if os.path.getsize(self.users_file) == 0:
            self.wallet_user_list = []
            return

        with open(self.users_file, 'r') as outfile:
            self.wallet_user_list = json.load(outfile)

        return self.wallet_user_list

    def create_user_wallet(self, user: UserRegistrationSchema):

        # Check if the file contains valid data or is empty
        with open(self.users_file, 'r') as f:
            contents = f.read().strip()  # read and remove any leading/trailing spaces

            # If the file is not empty
            if contents:
                try:
                    data = json.loads(contents)
                    if data:  # if the JSON is not an empty structure
                        existing_emails = {user['email'] for user in self.wallet_user_list}

                        if user.email in existing_emails:
                            error = f"The file already contains the user {user.email}."
                            logger.warning(error)
                            raise UserException(errors=error, message=error)

                        warning = "The file already contains users data."
                        logger.warning(warning)
                    else:
                        data = []
                except json.JSONDecodeError:
                    error = "The file doesn't contain valid JSON."
                    logger.error(error)
                    raise Exception(error)
            else:
                data = []

        logger.info(f'Creating new wallet: {user.email}')

        try:
            # Create wallet & account:
            wallet = WalletController(email=user.email, password=user.password)
            wallet.create_wallet(store_mnemonic=True)
            wallet.create_account(alias=user.email)
            # Get address & request tokens from faucet:
            address = wallet.get_address()["address"]["inner"]
            # self.faucet.request_tokens(address=address)
            # convert UserRegistrationSchema to dict
            user_dict = UserRegistrationSchema.model_dump(user)
            user_dict['address'] = address
            data.append(user_dict)
            logger.info(f'Creating new wallet: {user.email} ... Ok!')
        except Exception as e:
            logger.exception(f'Creating new wallet: {user.email} ... Failed! {e}')
            raise e

        with open(self.users_file, 'w') as outfile:
            json.dump(data, outfile, indent="\t")

        self.wallet_user_list = data
        return self.wallet_user_list

    def register_resource(self, user, resource_data):
        try:
            # -- login to market REST:
            self.controller.login(user['email'], user['password'])
            # -- Register resource:
            return self.controller.register_resource(resource_data=resource_data)
        except Exception as e:
            raise e

    def get_resource(self):
        # todo finalize this method
        # Initialize API controller:
        controller = ClientController()
        user = self.wallet_user_list[0]
        try:
            # -- login to market REST:
            controller.login(user['email'], user['password'])
            # -- Register resource:
            return controller.list_resources()
        except Exception as e:
            logger.exception(f"Unexpected error! {e}")
            raise e

    def delete_resource(self, resource_id):
        response = self.controller.delete_resource(resource_id=resource_id)
        if response['code'] not in [200, 201]:
            raise Exception(response['message'])

    def get_wallet_balances(self):
        balances = []
        for user in self.wallet_user_list:
            email = user["email"]
            password = user["password"]
            try:
                # Create wallet & account:
                wallet = WalletController(email=email,
                                          password=password).connect()
                balance = wallet.get_balance()
                logger.info(f'User {email} balance is {balance}')
                balances.append({'email': email, 'balance': balance})
            except Exception as e:
                logger.exception(
                    f'Failed to retrieve balance for user {email}! {e}')

        return balances

    def get_wallet_addresses(self):

        for user in self.wallet_user_list:
            logger.debug(f"Getting wallet addresses for user: {user['email']}")
            email = user["email"]
            password = user["password"]
            try:
                # Create wallet & account:
                wallet = WalletController(email=email,
                                          password=password).connect()
                address = wallet.get_address()["address"]["inner"]
                logger.info(f'User {email} address is {address}')
            except Exception as e:
                logger.exception(f'Failed to retrieve address for user {email}! {e}')

    def request_tokens(self, user):

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
        except Exception as e:
            logger.exception(f'Failed to request tokens for user {email}! {e}')

    def register_user(self, user: UserRegistrationSchema):

        self.controller = ClientController()

        logger.info(f"Registering user: {user.email}")
        try:
            # Register user:
            self.controller.register(
                email=user.email,
                password=user.password,
                password_conf=user.password_conf,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
            )

            logger.info(f"Registering user: {user.email} ... Ok!")

        except RegisterException as e:
            raise RegisterException(message=f"Failed to register user: {user.email}! {str(e.errors)}")

        return

    def send_measurements(self, user, data: MeasurementsSchema):

        logger.info(f"Posting data for user: {user['email']}")

        # -- login to market REST:
        self.controller.login(user['email'], user['password'])
        measurements = MeasurementsSchema.model_dump(data)
        try:
            response = self.controller.send_measurements(payload=measurements)
        except PostMeasurementsException as e:
            raise PostMeasurementsException(message=str(e), errors=str(e))
        logger.info(response)
        logger.info(f"Posting data for user: {user['email']} ... Ok!")
        return response

    def list_current_open_session(self, user):
        # Initialize API controller:
        try:
            # -- login to market REST:
            self.controller.login(user['email'], user['password'])
            # -- Get current last active session (status='closed'):
            session_data = self.controller.list_last_session(status='open')
            logger.info(json.dumps(session_data, indent=2))
            return session_data
        except MarketSessionException:
            logger.error("Unable to get information from market session.")
        except NoMarketSessionException:
            logger.error("There are no market sessions in 'open' state.")
        except BaseException as e:
            logger.exception(f"Unexpected error! {e}")

    def list_market_balance(self):
        # Initialize API controller:
        controller = ClientController()

        for user in self.wallet_user_list:
            logger.info(f"Getting balance for user {user['email']}")
            email = user["email"]
            password = user["password"]
            try:
                # -- login to market REST:
                controller.login(email, password)
                balance = controller.get_market_balance()
                logger.info(json.dumps(balance, indent=2))
                logger.info(f"Getting balance for user {user['email']} ... Ok!")
            except MarketSessionException:
                logger.error("Failed to get market balance.")
            except BaseException as e:
                logger.exception(f"Unexpected error! {e}")

    def list_market_bids(self, user, open_session_only=False):
        # Initialize API controller:
        controller = ClientController()
        bids_arr = []
        logger.info(f"Getting bids for user {user['email']}")

        email = user["email"]
        password = user["password"]
        active_session_id = None
        try:
            # -- login to market REST:
            self.controller.login(email, password)

            if open_session_only:
                # -- Get current last active session (status='closed'):
                session_data = controller.list_last_session(status='open')
                # Get session_id & fetch data for that session:
                active_session_id = session_data["market_session_id"]

            user_bids = controller.get_current_session_bids(session_id=active_session_id)
            if user_bids:
                bids_arr.append(user_bids)
            logger.info(f"Getting bids for user {user['email']} ... Ok!")
        except MarketBidException:
            logger.error("Failed to get market bids.")
        except BaseException as e:
            logger.exception(f"Unexpected error! {e}")

        logger.info(json.dumps(bids_arr, indent=2))
        return bids_arr

    def transfer_balance_to_address(self, address):
        for user in self.wallet_user_list:
            logger.info(f"Transferring user {user['email']} balance to firefly")
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
