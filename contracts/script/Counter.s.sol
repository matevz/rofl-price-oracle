// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {PriceFeedDirectory} from "../src/PriceFeedDirectory.sol";

contract PriceFeedScript is Script {
    PriceFeedDirectory public priceFeedDirectory;

    function setUp() public {}

    function run() public {
        vm.startBroadcast();

        // TODO
        priceFeedDirectory = new PriceFeedDirectory();

        vm.stopBroadcast();
    }
}
