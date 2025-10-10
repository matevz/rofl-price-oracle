# Oasis Price Oracle

## About

A simple python-based client that runs in ROFL that queries a centralized 
exchange and stores price quotes to the Sapphire smart contract. Multiple
exchanges and trading pairs are supported.

## Contracts

Solidity contracts for the price feed directory and a simple aggregator are 
located in the `contracts` folder. Move to that directory, then run:  

### Install dependencies

```shell
soldeer install
```

### Localnet

Localnet already has hardcoded accounts and ROFL app ids. To compile and deploy 
the price feed contract that keeps track of all aggregator contracts based 
on the app ID, exchange, and trading pair run:

```shell
forge create \
    --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
    --rpc-url http://localhost:8545 \
    --broadcast \
    PriceFeedDirectory
```

When running the oracle for the first time, it will deploy an appropriate 
aggregator contract and register it in the price feed directory.

Alternatively, you can compile and deploy a new aggregator contract directly by 
issuing:

```shell
forge create \
    --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
    --rpc-url http://localhost:8545 \
    --broadcast \
    SimpleAggregator \
    --constructor-args 000000000000000000000000000000000000000000 # your app ID in hex
```

### Testnet and Mainnet

Invoke commands above with:

```
--rpc-url https://testnet.sapphire.oasis.io
```

or

```
--rpc-url https://sapphire.oasis.io
```

### Running contract tests

1. Compile sapphire-foundry precompiles:

   ```shell
   pushd contracts/dependencies/@oasisprotocol-sapphire-foundry-0.1.2/precompiles
   cargo build --release
   popd
   ```

2. Now you can run the tests:

   ```shell
   cd contracts
   forge test
   ```

For more info see https://docs.oasis.io/build/tools/foundry

## Oasis price oracle

Python price oracle lives in the `oracle` folder.

1. Init python venv and install dependencies
   
   ```shell
   cd oracle
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Make sure you have your contracts compiled and ABIs ready in
   ../contracts/out/SimpleAggregator/PriceFeedDirectory.json
   and deployed.

3. For Localnet, the default price feed directory address will work and no 
   key management service is required. Simply run oracle:

   ```shell
   ./main.py
   ```

   For ROFL on Mainnet/Testnet where the key management service is available 
   at `/run/appd/appd.sock` Unix socket you can run:

   ```shell
   ./main.py --network sapphire-testnet
   ```
