// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {Oracle} from "../src/Oracle.sol";

contract OracleScript is Script {
    Oracle public oracle;

    function setUp() public {}

    function run() public {
        vm.startBroadcast();

        // TODO
        oracle = new Oracle(hex"000000000000000000000000000000000000000000");

        vm.stopBroadcast();
    }
}
