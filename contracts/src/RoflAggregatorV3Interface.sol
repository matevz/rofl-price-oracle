// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { AggregatorV3Interface } from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

interface RoflAggregatorV3Interface is AggregatorV3Interface {
    function getRoflAppId() external view returns (bytes21);
}