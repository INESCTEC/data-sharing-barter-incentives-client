import os

from loguru import logger
from dotenv import load_dotenv

load_dotenv('.env')

from src.AgentManager import AgentManager
# logger:
format = "{time:YYYY-MM-DD HH:mm:ss} | {level:<5} | {message}"
logger.add("files/logfile.log", format=format, level='DEBUG', backtrace=True)
logger.info("-" * 79)


def main():
    while True:
        _clear_console()
        print("     CLIENT MAIN MENU - Wallet Detected")
        print("1  - Market Operations")
        print("2  - Wallet Operations")
        _sep()
        print("0 - Exit")
        _empty()
        choice = input("Please make a choice: ")

        if choice == "1":
            market_menu()
        elif choice == "2":
            wallet_menu()
        elif choice == "0":
            exit("Exit.")
        else:
            print("Invalid option.")


def main_no_installation():
    while True:
        _clear_console()
        print("     CLIENT MAIN MENU - No Users Detected")
        print("1  - Create users wallets")
        _sep()
        print("0 - Exit")
        _empty()
        choice = input("Please make a choice: ")

        if choice == "1":
            installation_menu()
            main()
        elif choice == "0":
            exit("Exit.")
        else:
            print("Invalid option.")


def installation_menu():
    _clear_console()
    print("This will create a new market wallet & account for a "
          "predefined number of users.")
    choice = input("Proceed? (Y/n)")
    if choice.lower() == "y":
        nr_users = int(input("Define number of users to create: "))
        name_prefix = input("Define prefix of user names to use: ")
        ag = AgentManager()
        ag.create_user_wallets(nr_users=nr_users, name_prefix=name_prefix)

    input("Press ENTER to continue.")


def market_menu():
    ag = AgentManager()
    ag.load_available_users()

    while True:
        _clear_console()
        print("     Market OPS MENU")
        print("1  - Register users in market platform")
        print("2  - Send measurements data (past 24h)")
        print("3  - List open market session")
        print("4  - Place market bids")
        print("5  - List bids for current 'open' session")
        print("6  - Get current market balance")
        print("7  - List market bid history")
        _sep()
        print("9 - Return to previous menu.")
        print("0 - Exit")
        _empty()
        choice = input("Please make a choice: ")

        if choice == "1":
            # Register users:
            ag.register_users()
        if choice == "2":
            # Send measurements data (mock):
            ag.send_measurements()
        elif choice == "3":
            # List current open session:
            ag.list_current_open_session()
        elif choice == "4":
            # Place users bids:
            ag.place_bids()
        elif choice == "5":
            # List users bids for current open session:
            ag.list_market_bids(open_session_only=True)
        elif choice == "6":
            # List users market balance
            ag.list_market_balance()
        elif choice == "7":
            # List users bid history:
            ag.list_market_bids(open_session_only=False)
        elif choice == "9":
            return
        elif choice == "0":
            exit("Exit.")
        else:
            print("Invalid option.")

        input("Press ENTER to continue.")


def wallet_menu():
    ag = AgentManager()
    ag.load_available_users()

    while True:
        _clear_console()
        print("     Wallet OPS MENU")
        print("1  - Get wallet addresses")
        print("2  - Get wallet balances")
        print("3  - Transfer users wallet balances to address")
        print("4  - Request tokens from IOTA faucet")
        _sep()
        print("9 - Return to previous menu.")
        print("0 - Exit")
        _empty()
        choice = input("Please make a choice: ")

        if choice == "1":
            ag.get_wallet_addresses()
        elif choice == "2":
            ag.get_wallet_balances()
        elif choice == "3":
            out_address = input("Enter output address: ")
            ag.transfer_balance_to_address(address=out_address)
        elif choice == "4":
            ag.request_tokens()
        elif choice == "9":
            return
        elif choice == "0":
            exit("Exit.")
        else:
            print("Invalid option.")

        input("Press ENTER to continue.")


def _clear_console():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def _empty():
    print("")


def _sep():
    print("===========================================")


if __name__ == '__main__':
    users_file_dir = os.environ["USERS_FILE_DIR"]
    if not os.path.exists(users_file_dir):
        main_no_installation()
    else:
        main()
