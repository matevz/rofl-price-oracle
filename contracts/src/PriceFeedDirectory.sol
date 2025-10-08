// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "forge-std/console.sol";
import { Subcall } from "@oasisprotocol/sapphire-contracts/contracts/Subcall.sol";

import { RoflAggregatorV3Interface } from "./RoflAggregatorV3Interface.sol";
import { SimpleAggregator } from "./SimpleAggregator.sol";

/**
 * A directory contract for ROFL-powered price aggregator feeds.
 * Primarily used for bootstrapping ROFL-powered price oracles.
 */
contract PriceFeedDirectory {
    bytes16 private constant HEX_DIGITS = "0123456789abcdef";

    error AggregatorExists(bytes32 key);

    event FeedAdded(address indexed aggregator, bytes32 key, string providerChainPair);

    // Maps the hashed and lowercase hex-encoded app ID (without leading 0x), price provider hostname, (optional) chain and trading pair (or contract address without leading 0x) separated by / to the data feed.
    // Key examples:
    // - keccak256("005a216eb7f450bcc1f534a7575fb33d611b463fa2/bitstamp.net/btc_usd")
    // - keccak256("005a216eb7f450bcc1f534a7575fb33d611b463fa2/uniswap.org/polygon/native")
    // - keccak256("005a216eb7f450bcc1f534a7575fb33d611b463fa2/uniswap.org/base/833589fCD6eDb6E08f4c7C32D4f71b54bdA02913/1bfd67037b42cf73acf2047067bd4f2c47d9bfd6")
    mapping(bytes32 => RoflAggregatorV3Interface) public feeds;

    // List of public ROFL-powered aggregator contracts.
    RoflAggregatorV3Interface[] public discoverableFeeds;

    // Adds a new ROFL-powered price aggregator feed smart contract.
    // @param providerChainPair Hashed value of the exchange hostname + / + the
    //        trading pair.
    //        The trading pair is a lower case string defined as:
    //          - base currency + _ + quote currency
    //          - chain name + / + input currency address + / + output currency
    //            address
    //        The currency address is a lower-case hex-encoded address of an
    //        ERC-20 contract without the leading "0x" or "native", if it's a
    //        native token.
    //        Examples:
    //          - keccak256("bitstamp.net/btc_usd")
    //          - keccak256("uniswap.org/polygon/native/1bfd67037b42cf73acf2047067bd4f2c47d9bfd6")
    //          - keccak256("uniswap.org/base/833589fCD6eDb6E08f4c7C32D4f71b54bdA02913/1bfd67037b42cf73acf2047067bd4f2c47d9bfd6")
    // @param agg App-specific price aggregator smart contract.
    function addFeed(string calldata providerChainPair, RoflAggregatorV3Interface agg, bool discoverable) external {
        uint168 roflAppId = uint168(agg.getRoflAppId());
        // Convert roflAppId bytes to lowercase hex string (without 0x prefix).
        // Inspired by https://github.com/OpenZeppelin/openzeppelin-contracts/blob/92033fc08df1c8ebeb8046d084dd24e82ba9d065/contracts/utils/Strings.sol#L85
        bytes memory roflAppIdHex = new bytes(42);
        for (int8 i = 41; i >= 0; --i) {
            roflAppIdHex[uint8(i)] = HEX_DIGITS[roflAppId & 0xf];
            roflAppId >>= 4;
        }

        // Create the key by combining roflAppIdHex with providerChainPair
        bytes32 key = keccak256(abi.encodePacked(roflAppIdHex, "/", providerChainPair));

        if (address(feeds[key]) != address(0)) {
            revert AggregatorExists(key);
        }
        feeds[key] = agg;

        if (discoverable) {
            discoverableFeeds.push(agg);
        }

        emit FeedAdded(address(agg), key, providerChainPair);
    }
}
