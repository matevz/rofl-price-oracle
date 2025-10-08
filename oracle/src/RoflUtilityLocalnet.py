from web3 import Web3
from web3.types import TxParams

from .RoflUtilityInterface import RoflUtilityInterface

class RoflUtilityLocalnet(RoflUtilityInterface):
    def __init__(self, w3: Web3 = None):
        self.w3 = w3
        if w3 is None:
            self.w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

    def fetch_appid(self) -> str:
        return "rofl11qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtdv26p"

    def fetch_key(self, id: str) -> str:
        pass

    def submit_tx(self, tx: TxParams) -> str:
        # Sign and send the transaction
        tx_hash = self.w3.eth.send_transaction(tx)

        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Check if transaction was successful
        if tx_receipt['status'] == 1:
            return '{"data": "a1626f6b40"}'
        else:
            return '{"data": "a1646661696ca364636f646508666d6f64756c656365766d676d6573736167657272657665727465643a20614a416f4c773d3d"}'