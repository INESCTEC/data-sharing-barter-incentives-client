# -- For debug purposes. Not necessary when using docker containers
# from dotenv import load_dotenv
# load_dotenv(".env")


import os
import json
import click

from loguru import logger

from src.controller import ClientController
from src.generators import MeasurementsGenerator

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
              help='User email.',
              required=True,
              type=str)
@click.option('--password',
              help='User password.',
              required=True,
              type=str)
@click.option('--first_name',
              help='User first name.',
              required=True,
              type=str)
@click.option('--last_name',
              help='User last name.',
              required=True,
              type=str)
def register(email, password, first_name, last_name):
    logger.info(f'Registering user: {email}')
    # todo: reutilizar codigo.


@click.command()
@click.option('--email',
              help='User email.',
              required=True,
              type=str)
@click.option('--password',
              help='User password.',
              required=True,
              type=str)
@click.option('--bid_price',
              help='Market bid price (IOTA).',
              required=True,
              type=float)
@click.option('--bid_price',
              help='Market max payment price (IOTA).',
              required=True,
              type=float)
@click.option('--gain_func',
              help='User last name.',
              required=False,
              default='mse',
              type=str)
def place_bid(email, password, bid_price, max_payment, gain_func):
    logger.info(f'Placing bid for user: {email}')
    # todo: place bid
    #  1) get valorem address
    #  2) transfer tokens to address
    #  3) send validation to valorem


@click.command()
@click.option('--email',
              help='User email.',
              required=True,
              type=str)
@click.option('--password',
              help='User password.',
              required=True,
              type=str)
def get_forecasts(email, password):
    # todo: fetch forecasts from VALOREM platform and store it on user DB
    pass


@click.command()
@click.option('--email',
              help='User email.',
              required=True,
              type=str)
@click.option('--password',
              help='User password.',
              required=True,
              type=str)
def send_measurements(email, password):
    # todo: Creates mock measurements data & sends to VALOREM platform

    pass


@click.group()
@logger.catch
def cli():
    pass


cli.add_command(register)
cli.add_command(place_bid)
cli.add_command(get_forecasts)
cli.add_command(send_measurements)


if __name__ == '__main__':
    cli()
