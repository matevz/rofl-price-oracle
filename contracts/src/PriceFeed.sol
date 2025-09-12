// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { AggregatorV3Interface } from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";
import { Subcall } from "@oasisprotocol/sapphire-contracts/contracts/Subcall.sol";
import { SimpleAggregator } from "./SimpleAggregator.sol";

contract PriceFeed {
    mapping(string pair => mapping(bytes21 => AggregatorV3Interface)) public feeds;
    mapping(string pair => bytes21[]) public oracles;

    function addFeed(string memory pair, AggregatorV3Interface feed) external {
        bytes21 roflAppId = Subcall.getRoflAppId();
        require(address(feeds[pair][roflAppId]) == address(0), "Aggregator already exists");

        feeds[pair][roflAppId] = AggregatorV3Interface(feed);
        oracles[pair].push(roflAppId);
    }
}
