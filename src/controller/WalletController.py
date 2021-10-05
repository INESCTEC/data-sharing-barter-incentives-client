import os
import iota_wallet as iw

from .helpers.wallet_helper import transaction_report

NODE_URL = os.environ["IOTA_NODE_URL"]


class WalletController:
    nodes = [{"url": NODE_URL, "auth": None, "disabled": False}]
    USERS_FILE_DIR = os.environ["USERS_FILE_DIR"]
    local_pow = False

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.account_manager = None
        self.wallet_location = os.path.join(self.USERS_FILE_DIR,
                                            "wallet-cli-db",
                                            self.email)
        self.client_options = {
            "nodes": self.nodes,
            "local_pow": self.local_pow
        }

    def create_wallet(self, store_mnemonic=False):
        self.connect()
        self.account_manager.store_mnemonic('Stronghold')
        mnemonic = self.account_manager.generate_mnemonic()
        print(f"Your wallet mnemonic:\n{mnemonic}")
        if store_mnemonic:
            self.store_wallet_mnemonic(mnemonic)
            print(f"Your mnemonic was stored in {self.wallet_location}.")
        print("A new wallet DB was created.")

    def create_account(self, alias):
        account_initialiser = self.account_manager.create_account(
            self.client_options)
        account_initialiser.alias(alias)
        account = account_initialiser.initialise()
        print(f'Account created: {account.alias()}')

    def connect(self):
        self.account_manager = iw.AccountManager(
            storage_path=self.wallet_location,
            allow_create_multiple_empty_accounts=True
        )
        self.account_manager.set_stronghold_password(self.password)
        return self

    def store_wallet_mnemonic(self, mnemonic):
        """
        creates a wallet
        :return:
        """
        file_path = os.path.join(self.wallet_location, "mnemonic.txt")
        with open(file_path, "w") as f:
            f.write(mnemonic)

    def get_balance(self):
        account = self.account_manager.get_account(self.email)
        account.sync().execute()
        return account.balance()

    def get_address(self):
        """
        :return: address object
        """
        for _ in range(5):
            try:
                account = self.account_manager.get_account(self.email)
                account.sync().execute()
                return account.generate_address()
            except TimeoutError as e:
                raise e
            except ValueError as e:
                connection_refused = 'Connection refused'
                timeout_err = 'operation timeout'
                if connection_refused in str(e):
                    raise ConnectionRefusedError("Unable to communicate with node!")
                if timeout_err in str(e):
                    import time
                    time.sleep(5)
                    continue
        # todo log this
        raise Exception("It was not possible to generate the wallet address")

    def get_transaction_list(self):
        account = self.account_manager.get_account(self.email)
        account.sync().execute()
        data = transaction_report(account.list_messages())
        return data

    def transfer_tokens(self, amount, address):
        """
        :param amount:
        :param address:
        :return:
        """
        account = self.account_manager.get_account(self.email)
        account.sync().execute()
        transfer = iw.Transfer(
            amount=amount,
            address=address,
            remainder_value_strategy='ReuseAddress'
        )
        node_response = account.transfer(transfer)
        return node_response

    def restore(self, user):
        pass

    def backup(self, user):
        pass

