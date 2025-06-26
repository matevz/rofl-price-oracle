import bech32
import httpx
import json
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
    ROFL_SOCKET_PATH = "/run/rofl-appd.sock"

    def __init__(self, url: str = ''):
        self.url = url

    def _appd_get(self, path: str, payload: typing.Any) -> typing.Any:
        transport = None
        if self.url and not self.url.startswith('http'):
            transport = httpx.HTTPTransport(uds=self.url)
            print(f"Using HTTP socket: {self.url}")
        elif not self.url:
            transport = httpx.HTTPTransport(uds=self.ROFL_SOCKET_PATH)
            print(f"Using unix domain socket: {self.ROFL_SOCKET_PATH}")

        client = httpx.Client(transport=transport)

        url = self.url if self.url and self.url.startswith('http') else "http://localhost"
        print(f"  Getting {json.dumps(payload)} to {url+path}")
        response = client.get(url + path, json=payload, timeout=None)
        response.raise_for_status()
        return response

    def _appd_post(self, path: str, payload: typing.Any) -> typing.Any:
        transport = None
        if self.url and not self.url.startswith('http'):
            transport = httpx.HTTPTransport(uds=self.url)
            print(f"Using HTTP socket: {self.url}")
        elif not self.url:
            transport = httpx.HTTPTransport(uds=self.ROFL_SOCKET_PATH)
            print(f"Using unix domain socket: {self.ROFL_SOCKET_PATH}")

        client = httpx.Client(transport=transport)

        url = self.url if self.url and self.url.startswith('http') else "http://localhost"
        print(f"  Posting {json.dumps(payload)} to {url+path}")
        response = client.post(url + path, json=payload, timeout=None)
        response.raise_for_status()
        return response

    def fetch_appid(self) -> str:
        return "rofl1qqn9xndja7e2pnxhttktmecvwzz0yqwxsquqyxdf"
        # payload = {}
        #
        # path = '/rofl/v1/app/id'
        #
        # response = self._appd_post(path, payload)
        # return response

    def fetch_key(self, id: str) -> str:
        payload = {
            "key_id": id,
            "kind": "secp256k1"
        }

        path = '/rofl/v1/keys/generate'

        response = self._appd_post(path, payload).json()
        return response["key"]

    def submit_tx(self, tx: TxParams) -> str:
        payload = {
            "tx": {
                "kind": "eth",
                "data": {
                    "gas_limit": tx["gas"],
                    "value": tx["value"],
                    "data": tx["data"].lstrip("0x"),
                },
            },
            "encrypted": False,
        }

        # Contract create transactions don't have "to", others have it.
        if tx.get("to"):
            payload["tx"]["data"]["to"] = tx["to"].lstrip("0x")

        path = '/rofl/v1/tx/sign-submit'

        return self._appd_post(path, payload).json()