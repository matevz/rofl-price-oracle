from web3 import Web3
import json
from sapphirepy import sapphire
from pathlib import Path


class ContractUtility:
    """
    Initializes the ContractUtility class.

    :param network_name: Name of the network to connect to
    :type network_name: str
    :return: None
    """

    def __init__(self, network_name: str):
        networks = {
            "sapphire": "https://sapphire.oasis.io",
            "sapphire-testnet": "https://testnet.sapphire.oasis.io",
            "sapphire-localnet": "http://localhost:8545",
        }
        self.network = networks[network_name] if network_name in networks else network_name
        self.w3 = self.setup_web3_middleware()

    def setup_web3_middleware(self) -> Web3:
        provider = Web3.WebsocketProvider(self.network) if self.network.startswith("ws:") else Web3.HTTPProvider(self.network)
        return sapphire.wrap(Web3(provider))

    def get_contract(contract_name: str) -> (str, str):
        """Fetches ABI of the given contract from the contracts folder"""
        output_path = (Path(__file__).parent.parent.parent / "contracts" / "out" / f"{contract_name}.sol" / f"{contract_name}.json").resolve()
        contract_data = ""
        with open(output_path, "r") as file:
            contract_data = json.load(file)

        abi, bytecode = contract_data["abi"], contract_data["bytecode"]["object"]
        return abi, bytecode
