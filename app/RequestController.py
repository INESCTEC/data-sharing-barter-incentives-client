"""

This is a generic request controller. It is responsible for the communication
between the server and the client. You don't need to make changes to the
RequestController class, but you can if you want to. Make sure those changes
reflect a general purpose that can solve other similar problems and not a
specific one. The only thing you need to do is to change the base URL in the
external_open_api_request.py file to match your server.

Continue the work in the external_open_api_request.py file. You can use the RequestController class
to make requests to the server. You may create helper functions in other files
that can also meet general problem-solving.

author: andre.f.garcia@inesctec.pt

"""
import os
from datetime import datetime, timedelta

import requests
from loguru import logger
from sqlalchemy.orm import Session

from app.models.models import Token


class RequestController:
    # Set to True if you want to verify the SSL certificate or None to ignore
    verify = False
    no_auth_endpoints = {'api/token', 'api/user/register'}
    base_url = os.getenv("BASE_URL", "http://192.168.1.164:8081")

    def __init__(self, db: Session):

        self.db = db
        self.session = requests.Session()

    def get_latest_valid_token(self):
        return self.db.query(Token) \
            .filter(Token.expires_at > datetime.utcnow()) \
            .order_by(Token.expires_at.desc()) \
            .first()

    @staticmethod
    def add_token(db_session, token, expires_in=3600):
        expiration_time = datetime.utcnow() + timedelta(seconds=expires_in)
        new_token = Token(token=token, expires_at=expiration_time)
        db_session.add(new_token)
        db_session.commit()
        return new_token

    def _update_authorization_header(self, endpoint):
        # Update the authorization header with the latest valid token if
        # the endpoint requires authentication
        if endpoint in self.no_auth_endpoints:
            self.session.headers.pop('Authorization', None)
        else:
            token_obj = self.get_latest_valid_token()
            if token_obj:
                self.session.headers.update({'Authorization': f'Bearer {token_obj.token}'})
            else:
                # If no valid token is found, ensure 'Authorization' is not included
                self.session.headers.pop('Authorization', None)

    def request(self, method, endpoint,
                params=None, data=None,
                files=None,
                expected_status_code=None,
                headers=None,
                base_url=None,
                **kwargs):

        self._update_authorization_header(endpoint=endpoint)

        if base_url is None:
            base_url = self.base_url

        url = f"{base_url}/{endpoint}"
        logger.debug(f"method: {method} "
                     f"| url: {url} "
                     f"| params: {kwargs} "
                     f"| headers: {headers}")

        response = self.session.request(method, url,
                                        verify=self.verify,
                                        params=params,
                                        data=data,
                                        files=files,
                                        **kwargs)

        logger.debug(f"method: {method} "
                     f"| url: {url} "
                     f"| params: {kwargs} "
                     f"| data: {data}"
                     f"| headers: {headers} "
                     f"| status: {response.status_code}")

        if expected_status_code and response.status_code != expected_status_code:
            raise Exception(f"Expected status_code {expected_status_code}, "
                            f"but got {response.status_code},"
                            f"response {response.content}")

        return response

    def get(self, endpoint, **kwargs):
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.request('POST', endpoint, **kwargs)

    def patch(self, endpoint, **kwargs):
        return self.request('PATCH', endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self.request('PUT', endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.request('DELETE', endpoint, **kwargs)
