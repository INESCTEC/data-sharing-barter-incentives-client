# -- For debug purposes. Not necessary when using docker containers
# from dotenv import load_dotenv
# load_dotenv(".env")


import os
import click
import datetime as dt

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
@click.option('--role',
              help='User role.',
              required=True,
              type=click.Choice(['buyer', 'seller'], case_sensitive=True))
def register(email, password, first_name, last_name, role):
    role_dict = {"buyer": [1, 2], "seller": [2]}
    logger.info(f'Registering user: {email}')
    controller = ClientController()
    controller.register(
        email=email,
        password=password,
        password_conf=password,
        first_name=first_name,
        last_name=last_name,
        role=role_dict[role]
    )


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
    # initialize REST controller
    controller = ClientController()
    # login to market REST:
    controller.login(email, password)
    # Bid placement:
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
    # initialize REST controller
    controller = ClientController()
    # login to market REST:
    controller.login(email, password)
    # Bid placement:
    # todo: fetch forecasts from VALOREM REST and store it on user DB


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
    # initialize REST controller
    controller = ClientController()
    # login to market REST:
    controller.login(email, password)
    # Measurements generation:
    date_now = dt.datetime.utcnow()
    mg = MeasurementsGenerator()
    measurements = mg.generate_mock_data_sin(
        start_date=date_now - dt.timedelta(days=2),
        end_date=date_now,
    )
    # todo: convert to JSON & send measurements to VALOREM REST


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
