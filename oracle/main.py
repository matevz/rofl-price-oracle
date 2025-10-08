#!/usr/bin/env python3

from src.PriceOracle import DEFAULT_PRICE_FEED_ADDRESS, EXCHANGE_FETCHERS, PriceOracle
import argparse

def main():
    """
    Main method for the Python CLI tool.

    :return: None
    """
    parser = argparse.ArgumentParser(description="A Python CLI tool for compiling, deploying, and interacting with smart contracts.")

    parser.add_argument(
        "--address",
        dest="address",
        type=str,
        help="Address of the aggregator contract to interact with. If none provided, the contract is looked up in the price feed directory. If it doesn't exist there, then a new aggregator contract is deployed and registered",
    )

    parser.add_argument(
        "--price-feed-address",
        dest="price_feed_address",
        type=str,
        help="Address of price feed directory contract",
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
        default="btc_usd",
        type=str,
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
        default="bitstamp.net",
        type=str,
    )

    arguments = parser.parse_args()
    if arguments.fetch_period < 1:
        parser.error("--fetch-period must be at least 1 second")

    if arguments.submit_period < 6:
        parser.error("--submit-period must be at least 6 seconds")

    if arguments.price_feed_address is None:
        arguments.price_feed_address = DEFAULT_PRICE_FEED_ADDRESS[arguments.network]

    print(f"Starting price oracle service. Using aggregator contract {arguments.address} and price feed directory {arguments.price_feed_address} on {arguments.network}. Pair: {arguments.pair}, Exchange: {arguments.exchange}. Fetch period: {arguments.fetch_period}s, Submit period: {arguments.submit_period}s.")

    price_oracle = PriceOracle(
        arguments.address,
        arguments.price_feed_address,
        arguments.network, arguments.exchange,
        arguments.pair,
        int(arguments.fetch_period), int(arguments.submit_period),
    )
    price_oracle.run()

if __name__ == '__main__':
    main()
