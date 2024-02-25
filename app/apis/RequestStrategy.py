import json
import os
from typing import Any

import requests
from tsg_client.controllers import TSGController


class RequestStrategy:
    headers = {"Content-Type": "application/json; charset=utf-8"}
    base_url = os.environ['PREDICO_BASE_URL']

    def initialize(self):
        pass

    def make_request(self,
                     endpoint: str,
                     method: str,
                     data: Any = None,
                     headers: dict = None,
                     **kwargs) -> requests.Response:
        """Make a request and return the response."""
        raise NotImplementedError("Subclasses must implement this method")


class RequestsStrategy(RequestStrategy):

    def initialize(self):
        pass

    def make_request(self,
                     endpoint: str,
                     method: str,
                     data: Any = None,
                     headers: dict = None,
                     **kwargs) -> requests.Response:

        url = f"{os.environ['PREDICO_BASE_URL']}/api{endpoint}"

        # Validate method
        if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
            raise ValueError("Unsupported HTTP method")

        kwargs['headers'] = self.headers if headers is None else headers
        # Get the method from the requests module
        request_method = getattr(requests, method.lower())

        if method.lower() == 'get' and data:
            kwargs['params'] = data
        else:
            if data:
                kwargs['json'] = data

        return request_method(url=url, **kwargs)


class DataspaceStrategy(RequestStrategy):

    def __init__(self):
        self.conn = self.initialize()

    def initialize(self):
        return TSGController(
            api_key=os.environ['MY_CONNECTOR_API_KEY'],
            connector_id=os.environ['MY_CONNECTOR_ID'],
            access_url=os.environ['MY_CONNECTOR_ACCESS_URL'],
            agent_id=os.environ['MY_CONNECTOR_AGENT_ID']
        )

    def make_request(self,
                     endpoint: str,
                     method: str,
                     data: Any = None,
                     headers: dict = None,
                     **kwargs) -> requests.Response:

        api_version = os.environ['API_VERSION']
        headers = self.headers if headers is None else headers

        try:
            return self.conn.openapi_request(
                external_access_url=os.environ['EXTERNAL_ACCESS_URL'],
                external_connector_id=os.environ['EXTERNAL_CONNECTOR_ID'],
                api_version=api_version,
                endpoint=endpoint,
                headers=headers,
                data=json.dumps(data),
                method=method,
                **kwargs
            )
        except Exception as e:
            raise e


class RequestContext:
    def __init__(self, strategy: RequestStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: RequestStrategy):
        self._strategy = strategy

    def make_request(self,
                     endpoint: str,
                     method: str,
                     data: Any = None,
                     headers: dict = None,
                     **kwargs) -> requests.Response:

        return self._strategy.make_request(endpoint=endpoint,
                                           method=method,
                                           headers=headers,
                                           data=data,
                                           **kwargs)
