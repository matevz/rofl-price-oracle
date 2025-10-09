import cbor2
import typing
from web3 import Web3
from web3.types import TxParams

from .RoflUtility import RoflUtility

class RoflUtilityLocalnet(RoflUtility):
    def __init__(self, w3: Web3 = None):
        self.w3 = w3
        if w3 is None:
            self.w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

    def fetch_appid(self) -> str:
        return "rofl11qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqtdv26p"

    def fetch_key(self, id: str) -> str:
        pass

    def submit_tx(self, tx: TxParams) -> typing.Any:
        # Sign and send the transaction
        tx_hash = self.w3.eth.send_transaction(tx)

        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Check if transaction was successful
        if tx_receipt['status'] == 1:
            return {"data": cbor2.loads(bytes.fromhex("a1626f6b40")), "tx_receipt": tx_receipt}
        else:
            return {"tx_receipt": tx_receipt}