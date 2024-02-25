import argparse
import requests
from requests.exceptions import HTTPError
from loguru import logger
from typing import Optional
import sys

BASE_URL = 'http://localhost:8000'

# API Endpoints
LOGIN_ENDPOINT = f'{BASE_URL}/user/login'
GET_SESSION_ENDPOINT = f'{BASE_URL}/market/session'
BID_ENDPOINT = f'{BASE_URL}/market/session/bid'
RESOURCE_ENDPOINT = f'{BASE_URL}/user/resource'

logger.add("logs.log", format="{time} {level} {message}", level="INFO")

# Create a session object to maintain cookies across requests
session = requests.Session()


def login(credentials):
    try:
        auth = {"email": credentials['email'], "password": credentials['password']}
        response = session.post(LOGIN_ENDPOINT, json=auth)
        response.raise_for_status()
        # Parse the token from response if needed
        if response.status_code == 200:
            logger.success("Logged in successfully.")
            return
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')

    sys.exit()


def get_latest_session_data() -> Optional[dict]:
    try:
        response = session.get(GET_SESSION_ENDPOINT)
        response.raise_for_status()

        sessions = response.json().get('data', [])
        if not sessions:
            logger.error("No session data available.")
            return None

        # Sort sessions by session number in descending order and take the first one
        latest_session = sorted(sessions, key=lambda x: x['session_number'], reverse=True)[0]

        logger.info(f"Latest session retrieved: {latest_session['session_number']}")

        return {
            "session_id": latest_session['id'],
            "session_number": latest_session['session_number'],
            "market_price": int(latest_session['market_price']),
            "status": latest_session['status']
        }

    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')

    return None


def bid(session_data):
    try:
        if session_data['status'] != 'open':
            logger.error("Session is not open for bidding.")
            return False

        response = session.get(RESOURCE_ENDPOINT)
        for resource in response.json()['data']:

            # Construct the bid data from the session data
            bid_data = {
                "email": "andre.f.garcia@inesctec.pt",
                "bid_price": session_data['market_price'] * 1.5,
                "max_payment": session_data['market_price'] * 2,
                "resource": resource['id'],
                "market_session": session_data['session_number'],
                "gain_func": "mse"
            }
            response = session.post(BID_ENDPOINT, json=bid_data)
            if response.status_code == 202:
                logger.success(f"Bid placed for resource {resource['id']}.")
            else:
                logger.error(f"Failed to place bid for resource {resource['id']} "
                             f"with the following error: {response.json()['message']}")

            if response.status_code == 409:
                logger.error(response.json()['message'])

    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')


def main():
    # Login to the API to start a session
    parser = argparse.ArgumentParser(description='Login to API')
    parser.add_argument('--username', required=True, help='Username for login')
    parser.add_argument('--password', required=True, help='Password for login')
    args = parser.parse_args()

    user_credentials = {'email': args.username, 'password': args.password}

    login(user_credentials)

    # Get session data
    session_data = get_latest_session_data()

    # Use session data to place a bid
    bid(session_data)


if __name__ == "__main__":
    main()
