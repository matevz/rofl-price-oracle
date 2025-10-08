import asyncio
import requests
import sys

from .ContractUtility import ContractUtility
from .RoflUtility import bech32_to_bytes, RoflUtility
from .RoflUtilityLocalnet import RoflUtilityLocalnet


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
        response = requests.get(f'https://www.bitstamp.net/api/v2/ticker/{pair.replace('_','')}/')
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
    'binance.com': fetch_binance,
    'kraken.com': fetch_kraken,
    'coinbase.com': fetch_coinbase,
    'bitstamp.net': fetch_bitstamp,
}

# Predeployed price directory contract addresses based on the network.
DEFAULT_PRICE_FEED_ADDRESS = {
    "sapphire": None,
    "sapphire-testnet": None,
    "sapphire-localnet": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
}

class PriceOracle:
    def __init__(self,
                 address: str,
                 price_feed_address: str,
                 network_name: str,
                 exchange: str,
                 pair: str,
                 fetch_period: int,
                 submit_period: int):
        contract_utility = ContractUtility(network_name)
        abi, bytecode = ContractUtility.get_contract('SimpleAggregator')
        price_feed_abi, _ = ContractUtility.get_contract('PriceFeedDirectory')


        self.pair = pair
        self.fetch_period = fetch_period
        self.submit_period = submit_period
        self.exchange = exchange
        self.contract = contract_utility.w3.eth.contract(address=address, abi=abi, bytecode=bytecode)
        self.price_feed_contract = contract_utility.w3.eth.contract(address=price_feed_address, abi=price_feed_abi)
        self.w3 = contract_utility.w3
        self.rofl_utility = RoflUtilityLocalnet(self.w3) if network_name == "sapphire-localnet" else RoflUtility()

    def detect_or_deploy_contract(self):
        # Fetch the current app ID
        app_id = self.rofl_utility.fetch_appid()
        app_id_bytes = bech32_to_bytes(app_id)

        if self.contract.address is not None:
            return

        address = self.price_feed_contract.functions.feeds(
            self.w3.keccak(
                text="/".join((app_id_bytes.hex(), self.exchange, self.pair))
            )
        ).call()
        if address != '0x0000000000000000000000000000000000000000':
            self.contract = self.w3.eth.contract(address=address, abi=self.contract.abi)
            print(f"Detected aggregator contract {address}")
            return

        # Deploy the contract
        tx_params = self.contract.constructor(app_id_bytes).build_transaction({
            'gasPrice': self.w3.eth.gas_price,
        })

        print(tx_params, file=sys.stderr)
        result = self.rofl_utility.submit_tx(tx_params)
        print(f"Contract deployed. Result: {result}")

        # Update contract instance with deployed address
        self.contract = self.w3.eth.contract(
            address=tx_receipt.contractAddress, # todo
            abi=self.contract.abi,
            bytecode=self.contract.bytecode
        )

        tx = self.price_feed_contract.add_feed(
            self.w3.keccak(
                text="/".join((self.exchange, self.pair, self.contract.address))
            )
        )
        tx.wait()


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
            obs = (0, int(price * 10**10), int(last_submit), int(asyncio.get_event_loop().time()))
            print(f"{self.pair} Price: ${price:.2f}")
            observations.append(obs)

            if asyncio.get_event_loop().time() - last_submit > self.submit_period:
                self.submit_observations(observations)
                last_submit = asyncio.get_event_loop().time()
                observations = []

            await asyncio.sleep(self.fetch_period)

    def run(self) -> None:
        if not self.contract.address:
            self.detect_or_deploy_contract()

        # Subscribe to PromptSubmitted event
        # Create a new event loop first
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                asyncio.gather(self.observations_loop(2)))
        finally:
            loop.close()

    def submit_observations(self, observations: list):
        # Build the transaction
        tx_params = self.contract.functions.submitObservation(
            observations[-1][0],
            observations[-1][1],
            observations[-1][2],
            observations[-1][3]
        ).build_transaction({
            'gasPrice': self.w3.eth.gas_price,
            'gas': max(3000000, 1000*len(observations))
        })

        result = self.rofl_utility.submit_tx(tx_params)
        print(f"Submitted observations. Result: {result}")