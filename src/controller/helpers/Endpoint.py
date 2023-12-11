from dataclasses import dataclass
from collections import namedtuple

fields = ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'uri')
endpoint = namedtuple('endpoint', fields, defaults=(None,) * len(fields))

# HTTP methods
http_methods = "GET", "POST", "PUT", "DELETE", "PATCH"

# Authentication
login = endpoint(*http_methods, "/api/token/login")
register = endpoint(*http_methods, "/api/user/register")
wallet_address = endpoint(*http_methods, "/api/user/wallet-address")

# Market endpoints
market_bid = endpoint(*http_methods, "/api/market/bid")
market_bid_with_id = endpoint(*http_methods, "/api/market/bid/{bid_id}")
market_session = endpoint(*http_methods, "/api/market/session")
market_wallet_address = endpoint(*http_methods, "/api/market/wallet-address")
market_balance = endpoint(*http_methods, "/api/market/balance")
resource = endpoint(*http_methods, "/api/user/resource")

# Data endpoints
raw_measurements = endpoint(*http_methods, "/api/data/raw-data")


@dataclass(frozen=True)
class Endpoint:
    http_method: str
    uri: str
