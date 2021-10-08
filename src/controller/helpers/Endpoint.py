from dataclasses import dataclass
from collections import namedtuple

fields = ('GET', 'POST', 'PUT', 'DELETE', 'uri')
endpoint = namedtuple('endpoint', fields, defaults=(None,) * len(fields))

# HTTP methods
http_methods = "GET", "POST", "PUT", "DELETE",

# Authentication
login = endpoint(*http_methods, "/api/token/login")
register = endpoint(*http_methods, "/api/user/register")
wallet_address = endpoint(*http_methods, "/api/user/wallet-address")

# Market endpoints
market_bid = endpoint(*http_methods, "/api/market/bid")
market_session = endpoint(*http_methods, "/api/market/session")
market_wallet_address = endpoint(*http_methods, "/api/market/wallet-address")
market_balance = endpoint(*http_methods, "/api/market/balance")


@dataclass(frozen=True)
class Endpoint:
    http_method: str
    uri: str
