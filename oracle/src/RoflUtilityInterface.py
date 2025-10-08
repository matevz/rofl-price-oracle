from web3.types import TxParams

class RoflUtilityInterface:
    def fetch_appid(self) -> str:
        pass

    def fetch_key(self, id: str) -> str:
        pass

    def submit_tx(self, tx: TxParams) -> str:
        pass