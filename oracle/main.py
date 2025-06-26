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
        dest="contract_address",
        type=str,
        help="Address of the existing smart contract to interact with. If none provided, a new contract will be deployed",
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
        dest="fetch_period",
        help="Amount of seconds between fetching token prices (minimum value 1)",
        default=3,
        type=int,
    )

    parser.add_argument(
        "--submit-period",
        dest="submit_period",
        help="Amount of seconds between submitting observations on-chain (minimum value 6)",
        default=12,
        type=int,
    )

    parser.add_argument(
        "--exchange",
        help="Name of the exchange (" + ", ".join(EXCHANGE_FETCHERS.keys()) + ")",
    )

    arguments = parser.parse_args()
    if arguments.fetch_period < 1:
        parser.error("--fetch-period must be at least 1 second")

    if arguments.submit_period < 6:
        parser.error("--submit-period must be at least 6 seconds")


    print(f"Starting price oracle service. Using contract {arguments.contract_address} on {arguments.network}. Pair: {arguments.pair}, Exchange: {arguments.exchange}. Fetch period: {arguments.fetch_period}s, Submit period: {arguments.submit_period}s.")
    rofl_utility = RoflUtility()

    price_oracle = PriceOracle(arguments.contract_address,
                              arguments.network, arguments.exchange,
                              arguments.pair,
                              int(arguments.fetch_period), int(arguments.submit_period),
                              rofl_utility)
    price_oracle.run()

if __name__ == '__main__':
    main()
