# Chat bot contracts

## Localnet

Localnet has hardcoded accounts and ROFL app ids, so you can simply run:

```shell
forge create \
    --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
    --rpc-url http://localhost:8545 \
    --broadcast \
    PriceFeed
forge create \
    --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
    --rpc-url http://localhost:8545 \
    --broadcast \
    SimpleAggregator \
    --constructor-args 00d795c033fb4b94873d81b6327f5371768ffc6fcf
```

You can then submit a prompt from the CLI by issuing:

```shell
cast send 0x5FbDB2315678afecb367f032d93F642f64180aa3 \
    "addFeed(string,address)" "BTCUSD" "" \
    --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
    --rpc-url http://localhost:8545
```

## Testnet and Mainnet

First convert your `rofl1` app ID to hex, for example by using
https://slowli.github.io/bech32-buffer/

Then repeat the procedure above and use

```
--rpc-url https://testnet.sapphire.oasis.io
```

or

```
--rpc-url https://sapphire.oasis.io
```