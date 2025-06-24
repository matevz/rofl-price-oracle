import asyncio
import requests

from .ContractUtility import ContractUtility
from .RoflUtility import bech32_to_hex, RoflUtility


async def fetch_binance(pair: str) -> float:
    try:
        response = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={pair}')
        if response.status_code == 200:
            data = response.json()
            price = float(data['price'])

            # Store price with timestamp
            return price
        else:
            print(f"Error fetching price: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching Binance price: {e}")

async def fetch_coinbase(pair: str) -> float:
    try:
        response = requests.get(f'https://api.coinbase.com/v2/exchange-rates?currency={pair}')
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'rates' in data['data']:
                # Coinbase returns rates with currency codes as keys
                # For trading pairs like BTCUSD, we need to extract the quote currency
                rates = data['data']['rates']
                if 'USD' in rates:
                    price = float(rates['USD'])
                else:
                    # Fallback to first available rate
                    price = float(list(rates.values())[0])

                # Store price with timestamp
                return price
            else:
                print(f"Error fetching price: {data.get('error', 'Unknown error')}")
        else:
            print(f"Error fetching price: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching Coinbase price: {e}")

async def fetch_kraken(pair: str) -> float:
    try:
        response = requests.get(f'https://api.kraken.com/0/public/Ticker?pair={pair}')
        if response.status_code == 200:
            data = response.json()
            if 'result' in data:
                # Kraken returns results with pair names as keys
                pair_data = list(data['result'].values())[0]
                price = pair_data['c'][0]  # 'c' is the last trade closed array

                # Store price with timestamp
                return float(price)
            else:
                print(f"Error fetching price: {data.get('error', 'Unknown error')}")
        else:
            print(f"Error fetching price: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching Kraken price: {e}")

async def fetch_bitstamp(pair: str) -> float:
    try:
        response = requests.get(f'https://www.bitstamp.net/api/v2/ticker/{pair}/')
        if response.status_code == 200:
            data = response.json()
            if 'last' in data:
                # Bitstamp returns the last price directly
                price = data['last']

                # Store price with timestamp
                return float(price)
            else:
                print(f"Error fetching price: {data.get('error', 'Unknown error')}")
        else:
            print(f"Error fetching price: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching Bitstamp price: {e}")

EXCHANGE_FETCHERS = {
    'binance': fetch_binance,
    'kraken': fetch_kraken,
    'coinbase': fetch_coinbase,
    'bitstamp': fetch_bitstamp,
}


class PriceOracle:
    def __init__(self,
                 contract_address: str,
                 network_name: str,
                 exchange: str,
                 pair: str,
                 fetch_period: int,
                 submit_period: int,
                 rofl_utility: RoflUtility):
        contract_utility = ContractUtility(network_name, secret)
        abi, bytecode = ContractUtility.get_contract('Oracle')

        self.pair = pair
        self.fetch_period = fetch_period
        self.submit_period = submit_period
        self.exchange = exchange
        self.rofl_utility = rofl_utility
        self.contract = contract_utility.w3.eth.contract(address=contract_address, abi=abi, bytecode=bytecode)
        self.w3 = contract_utility.w3

    def deploy_contract(self):
        # Fetch the current app ID
        app_id = self.rofl_utility.fetch_appid()
        app_id_hex = bech32_to_hex(app_id)

        # Deploy the contract
        tx_params = self.contract.constructor(app_id_hex).build_transaction({
            'gasPrice': self.w3.eth.gas_price,
        })

        tx_hash = self.rofl_utility.submit_tx(tx_params)
        print(f"Got receipt {tx_hash} {dir(tx_hash)}")
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Contract deployed. Transaction hash: {tx_receipt.transactionHash.hex()}")
        print(f"Contract address: {tx_receipt.contractAddress}")

        # Update contract instance with deployed address
        self.contract = self.w3.eth.contract(
            address=tx_receipt.contractAddress,
            abi=self.contract.abi,
            bytecode=self.contract.bytecode
        )


    async def observations_loop(self, poll_interval):
        # Initialize price storage
        observations = []  # List of (uint256 price, uint64 timestamp) tuples
        last_submit = asyncio.get_event_loop().time()
        print(f"Starting price observation loop for {self.pair}...")

        # Price fetching loop
        while True:
            if not EXCHANGE_FETCHERS[self.exchange]:
                print(f"Unknown exchange: {self.exchange}")
                break

            price = await EXCHANGE_FETCHERS[self.exchange](self.pair)
            obs = (int(price * 10**10), int(asyncio.get_event_loop().time()))
            print(f"{self.pair} Price: ${price:.2f}")
            observations.append(obs)

            if asyncio.get_event_loop().time() - last_submit > self.submit_period:
                self.submit_observations(observations)
                last_submit = asyncio.get_event_loop().time()
                observations = []

            await asyncio.sleep(self.fetch_period)

    def run(self) -> None:
        self.deploy_contract()

        # Subscribe to PromptSubmitted event
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(self.observations_loop(2)))
        finally:
            loop.close()

    def submit_observations(self, observations: list):
        tx_hash = self.contract.functions.submitObservations(observations, self.contract.address).transact({'gasPrice': self.w3.eth.gas_price, 'gas': max(3000000, 1000*len(observations))})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Submitted observations. Transaction hash: {tx_receipt.transactionHash.hex()}")