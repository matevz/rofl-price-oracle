// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {PriceFeed} from "../src/PriceFeed.sol";

contract PriceFeedScript is Script {
    PriceFeed public priceFeed;

    function setUp() public {}

    function run() public {
        vm.startBroadcast();

        // TODO
        priceFeed = new PriceFeed();

        vm.stopBroadcast();
    }
}
