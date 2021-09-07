# -- For debug purposes. Not necessary when using docker containers
# from dotenv import load_dotenv
# load_dotenv(".env")


import os
import json
import click

from loguru import logger

from src.controller import WalletController
from src.controller import FaucetController


# -- Init Logger(s):
logs_dir = os.path.join("files", "logs")
logger.add(os.path.join(logs_dir, "info.log"),
           format="{time:YYYY-MM-DD HH:mm:ss} | {level:<5} | {message}",
           rotation="1 day",
           level='INFO',
           compression="zip",
           backtrace=True)
logger.info("-" * 70)
logger.info("-" * 70)


@click.command()
@click.option('--email',
              help='IOTA wallet account email.',
              required=True,
              type=str)
@click.option('--store_mnemonic',
              help='0 - does not save mnemonic / 1 - store mnemonic (debug).',
              required=False,
              type=click.Choice(['0', '1']),
              default='0')
def create_wallet(email, store_mnemonic):
    logger.info(f'Creating new wallet: {email}')
    wallet = WalletController(email=email)
    wallet.create_wallet(store_mnemonic=bool(int(store_mnemonic)))
    wallet.create_account(alias=email)


@click.command()
@click.option('--email',
              help='IOTA wallet account email.',
              required=True,
              type=str)
def get_address(email):
    logger.info(f'Getting address for account: {email}')
    wallet = WalletController(email=email).connect()
    address = wallet.get_address()["address"]["inner"]
    logger.info(address)
    logger.info(f'Getting address for account: {email} ... Ok!')
    return address


@click.command()
@click.option('--email',
              help='IOTA wallet account email.',
              required=True,
              type=str)
def get_balance(email):
    logger.info(f'Getting balance for account: {email}')
    wallet = WalletController(email=email).connect()
    balance = wallet.get_balance()
    logger.info(balance)
    logger.info(f'Getting balance for account: {email} ... Ok!')
    return balance


@click.command()
@click.option('--email',
              help='IOTA wallet account email.',
              required=True,
              type=str)
def list_transactions(email):
    logger.info(f'Listing transactions for account: {email}')
    wallet = WalletController(email=email).connect()
    transact = wallet.get_transaction_list()["transactions_resumed"]
    logger.info(json.dumps(transact, indent=3))
    logger.info(f'Listing transactions for account: {email} ... Ok!')


@click.command()
@click.option('--email',
              help='IOTA wallet account email.',
              required=True,
              type=str)
def request_funds(email):
    logger.info(f'Requesting funds to account: {email}')
    wallet = WalletController(email=email).connect()
    faucet = FaucetController()
    address = wallet.get_address()["address"]["inner"]
    logger.info(address)
    response = faucet.request_tokens(address=address)
    logger.info(response)
    logger.info(f'Requesting funds to account: {email} ... Ok!')


@click.command()
@click.option('--email',
              help='IOTA wallet account email.',
              required=True,
              type=str)
@click.option('--amount',
              help='Amount of IOTAs to transfer',
              required=True,
              type=int)
@click.option('--to_address',
              help='IOTA wallet address to send funds to.',
              required=True,
              type=str)
def send_tokens(email, amount, to_address):
    logger.info(f'Sending {amount}i from account {email} '
                f'to address {to_address}')
    wallet = WalletController(email=email).connect()
    wallet.transfer_tokens(amount=int(amount), address=to_address)
    logger.info(f'Sending {amount}i from account {email} '
                f'to address {to_address} ... Ok!')


@click.group()
@logger.catch
def cli():
    pass


cli.add_command(create_wallet)
cli.add_command(get_address)
cli.add_command(get_balance)
cli.add_command(list_transactions)
cli.add_command(request_funds)
cli.add_command(send_tokens)


if __name__ == '__main__':
    cli()
