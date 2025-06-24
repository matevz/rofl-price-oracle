#!/usr/bin/env python3

from src.PriceOracle import EXCHANGE_FETCHERS, PriceOracle
from src.RoflUtility import RoflUtility
import argparse

def main():
    """
    Main method for the Python CLI tool.

    :return: None
    """
    parser = argparse.ArgumentParser(description="A Python CLI tool for compiling, deploying, and interacting with smart contracts.")

    parser.add_argument(
        "--contract-address",
        type=str,
        help="Address of the existing smart contract to interact with. If none provided, a new contract will be deployed"
    )

    parser.add_argument(
        "--network",
        help="Chain name to connect to "
             "(sapphire, sapphire-testnet, sapphire-localnet)",
        default="sapphire-localnet",
    )

    parser.add_argument(
        "--pair",
        help="Trading pair to observe",
    )

    parser.add_argument(
        "--fetch-period",
        help="Amount of seconds between fetching token prices",
        default=3,
    )

    parser.add_argument(
        "--submit-period",
        help="Amount of seconds between submitting observations on-chain",
        default=12,
        min=6
    )

    parser.add_argument(
        "--exchange",
        help="Name of the exchange (" + ", ".join(EXCHANGE_FETCHERS.keys()) + ")",
        default=12,
        min=6
    )

    arguments = parser.parse_args()

    print(f"Starting price oracle service. Using contract {arguments.contract_address} on {arguments.network}. Pair: {arguments.pair}, Exchange: {arguments.exchange}. Fetch period: {arguments.fetch_period}s, Submit period: {arguments.submit_period}s.")    rofl_utility = RoflUtility()

    priceOracle = PriceOracle(arguments.contract_address,
                              arguments.network, arguments.exchange,
                              arguments.pair,
                              int(arguments.fetch_period), int(arguments.submit_period),
                              rofl_utility)
    priceOracle.run()

if __name__ == '__main__':
    main()
