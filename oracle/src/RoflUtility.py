from abc import abstractmethod
import bech32
import typing
from web3.types import TxParams

def bech32_to_bytes(app_id: str) -> bytes:
    """Decode the app_id from bech32 to 21-bytes as hex"""
    hrp, data = bech32.bech32_decode(app_id)
    if data is None:
        raise ValueError(f"Invalid bech32 app_id: {app_id}")

    # Convert 5-bit groups to bytes
    app_id_bytes = bech32.convertbits(data, 5, 8, False)
    if app_id_bytes is None:
        raise ValueError(f"Failed to convert app_id to bytes: {app_id}")

    # Convert bytes to hex string
    return bytes(app_id_bytes)


class RoflUtility:
    @abstractmethod
    def fetch_appid(self) -> str:
        pass

    @abstractmethod
    def fetch_key(self, id: str) -> str:
        pass

    @abstractmethod
    def submit_tx(self, tx: TxParams) -> typing.Any:
        pass