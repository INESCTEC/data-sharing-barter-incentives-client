import os
from datetime import datetime

import numpy as np
import pandas as pd
from payment.PaymentGateway.EthereumPayment.EthereumSmartContract import (SmartContractConfig,
                                                                          TokenABI)
from payment.PaymentGateway.IOTAPayment.IOTAPayment import WalletConfig
from sqlalchemy.orm import Session

from app.crud import get_token
from app.models.models import Token


def generate_data(csv_path: str):
    # Define the start date
    today = datetime.today()
    start_date = today - pd.Timedelta(days=30)  # 30 days ago

    # Generate a date range for one month with hourly frequency
    # One month of hourly data
    date_range = pd.date_range(start_date.strftime('%Y-%m-%d'), periods=24 * 30, freq='H')

    # Generate random values for the 'value' column
    np.random.seed(0)  # For reproducibility
    values = np.random.uniform(1.0, 10.0, size=len(date_range))

    # Create a DataFrame
    data = {
        'value': values,
        'datetime': date_range
    }
    df = pd.DataFrame(data)

    # Save DataFrame to CSV

    df.to_csv(csv_path, index=False)


def smart_contract_config() -> SmartContractConfig:
    return SmartContractConfig(
        contract_address=os.getenv("CONTRACT_ADDRESS"),
        abi=TokenABI.ETK)


def wallet_config() -> WalletConfig:
    # todo - move this to a ENV file
    return WalletConfig(
        node_url=["https://api.testnet.shimmer.network"],
        faucet_url="https://faucet.testnet.shimmer.network/api/enqueue",
        wallet_db_path=os.path.join('files', 'payment.db'),
        stronghold_snapshot_path=os.path.join('files', 'stronghold.snapshot'),
        file_dir=os.path.join('files'),
        wallet_backup_path=os.path.join('files', 'backup.db'),
        wallet_password="your_wallet_password"
    )


def transaction_to_dict(transaction):
    return {
        "type": transaction.payload.get('type'),
        "essence": transaction.payload.get('essence'),
        "unlocks": transaction.unlocks,
        "inclusionState": transaction.inclusionState,
        "timestamp": transaction.timestamp,
        "transactionId": transaction.transactionId,
        "networkId": transaction.networkId,
        "incoming": transaction.incoming,
        "note": transaction.note,
        "blockId": transaction.blockId
    }


def get_header(db: Session) -> dict:
    token: Token = get_token(db)
    if not token:
        return {"Content-Type": "application/json"}
    return {"Authorization": f"Bearer {token.token}", "Content-Type": "application/json"}
