import os

from payment.PaymentGateway.IOTAPayment.IOTAPaymentController import WalletConfig
from payment.PaymentGateway.EthereumSmartContract.EthereumSmartContract import SmartContractConfig, TokenABI
from app.models.models import Token
from app.crud import get_token
from sqlalchemy.orm import Session


def smart_contract_config() -> SmartContractConfig:
    return SmartContractConfig(
        web3_provider_url=os.getenv("WEB3_PROVIDER_URL"),
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
