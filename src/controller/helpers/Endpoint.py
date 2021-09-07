from dataclasses import dataclass
from collections import namedtuple

fields = ('GET', 'POST', 'PUT', 'DELETE', 'uri')
endpoint = namedtuple('endpoint', fields, defaults=(None,) * len(fields))

# HTTP methods
http_methods = "GET", "POST", "PUT", "DELETE",

# Authentication
login = endpoint(*http_methods, "/api/token/login")
register = endpoint(*http_methods, "/api/user/register")

# Market endpoints
market_bid = endpoint(*http_methods, "/api/market/bid")

# Wallet endpoints:
wallet_withdraw = endpoint(*http_methods, "/api/wallet/withdraw")


@dataclass(frozen=True)
class Endpoint:
    http_method: str
    uri: str
