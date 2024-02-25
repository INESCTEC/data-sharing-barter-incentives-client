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
from typing import Dict

import requests
from sqlalchemy.orm import Session

from app.crud import get_token, cleanup_expired_tokens
from app.models.models import Token


class RequestController:
    # Set to True if you want to verify the SSL certificate or None to ignore
    verify = False

    NO_AUTH_ENDPOINTS = {'api/token', 'api/user/register', 'api/test'}
    PREDICO_BASE_URL = os.getenv("PREDICO_BASE_URL", "http://predico02.inesctec.pt")
    USE_DATASPACE = os.getenv("USE_DATASPACE", "True").lower() == "true"

    EXTERNAL_ACCESS_URL = os.getenv('EXTERNAL_ACCESS_URL')
    EXTERNAL_CONNECTOR_ID = os.getenv('EXTERNAL_CONNECTOR_ID')
    MY_CONNECTOR_API_KEY = os.getenv("MY_CONNECTOR_API_KEY")
    MY_CONNECTOR_ACCESS_URL = os.getenv("MY_CONNECTOR_ACCESS_URL")
    MY_CONNECTOR_AGENT_ID = os.getenv("MY_CONNECTOR_AGENT_ID")
    MY_CONNECTOR_CONNECTOR_ID = os.getenv("MY_CONNECTOR_CONNECTOR_ID")

    def __init__(self, db: Session):

        self.db = db
        self.session = requests.Session()
        self.tsg_controller = self._init_tsg_controller() if self.USE_DATASPACE else None

    def _init_tsg_controller(self):
        from tsg_client.controllers import TSGController
        return TSGController(api_key=self.MY_CONNECTOR_API_KEY,
                             connector_id=self.MY_CONNECTOR_CONNECTOR_ID,
                             access_url=self.MY_CONNECTOR_ACCESS_URL,
                             agent_id=self.MY_CONNECTOR_AGENT_ID)

    def add_token(self, token, expires_in=3600) -> Token:
        expiration_time = datetime.utcnow() + timedelta(seconds=expires_in)
        new_token = Token(token=token, expires_at=expiration_time)
        self.db.add(new_token)
        self.db.commit()
        self.db.close()
        return new_token

    def _get_headers(self, endpoint: str) -> Dict[str, str]:
        headers = {"Content-Type": "application/json; charset=utf-8"}
        if endpoint not in self.NO_AUTH_ENDPOINTS:
            token_obj = get_token(self.db)
            if token_obj:
                headers['Authorization'] = f'Bearer {token_obj.token}'
        return headers

    def _prepare_request(self, endpoint: str, method: str, **kwargs) -> requests.Response:

        headers = self._get_headers(endpoint)
        url = f"{self.PREDICO_BASE_URL}/{endpoint}"
        if self.USE_DATASPACE and self.tsg_controller:
            response = self.tsg_controller.openapi_request(
                external_access_url=self.EXTERNAL_ACCESS_URL,
                external_connector_id=self.EXTERNAL_CONNECTOR_ID,
                api_version="1.0.0",
                endpoint=endpoint,
                headers=headers,
                method=method,
                **kwargs)
        else:
            response = self.session.request(method,
                                            url,
                                            verify=self.verify,
                                            headers=headers,
                                            **kwargs)
        return response

    def request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        try:
            return self._prepare_request(endpoint, method, **kwargs)
        except Exception as e:
            raise e

    def get(self, endpoint, **kwargs):
        return self.request('get', endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.request('post', endpoint, **kwargs)

    def patch(self, endpoint, **kwargs):
        return self.request('patch', endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self.request('put', endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.request('delete', endpoint, **kwargs)
