// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Observation, Oracle} from "../src/Oracle.sol";
import {Subcall} from "@oasisprotocol/sapphire-contracts/contracts/Subcall.sol";
import {Test, console} from "forge-std/Test.sol";

contract OracleTest is Test {
    Oracle public oracle;
    address public user;
    address public _oracle;
    string public domain;

    function setUp() public {
        _oracle = address(0x123);
        user = address(0x456);
        bytes21 roflAppID = bytes21(0);
        oracle = new Oracle(roflAppID);
    }

    function test_submitObservation() public {
        vm.startPrank(user);

        Observation[] memory observations = new Observation[](5);
        observations[0] = Observation({
            price: 45000,
            timestamp: 1751644800
        });
        observations[1] = Observation({
            price: 46500,
            timestamp: 1751648400
        });
        observations[2] = Observation({
            price: 47200,
            timestamp: 1751652000
        });
        observations[3] = Observation({
            price: 46800,
            timestamp: 1751655600
        });
        observations[4] = Observation({
            price: 48100,
            timestamp: 1751659200
        });
        oracle.submitObservations(keccak256("BTCUSD"), observations);

        Observation memory obs = oracle.getLastObservation("BTCUSD");
        assertEq(obs.price, 48100);
        assertEq(obs.timestamp, 1751659200);

        Observation[] memory resultObs = oracle.getObservations("BTCUSD", 0, observations.length);
        assertEq(resultObs.length, observations.length);
        for (uint256 i = 0; i < observations.length; i++) {
            assertEq(resultObs[i].price, observations[i].price);
            assertEq(resultObs[i].timestamp, observations[i].timestamp);
        }

        resultObs = oracle.getObservations("BTCUSD", 0, 0);
        resultObs = oracle.getObservations("BTCUSD", 0, 10);
        resultObs = oracle.getObservations("BTCUSD", 1, 10);
        resultObs = oracle.getObservations("BTCUSD", -1, 10);
        resultObs = oracle.getObservations("BTCUSD", -1, 5);

        vm.stopPrank();
    }

    function test_Revert_wrongTimestamp() public {
        vm.expectRevert(Oracle.TimestampSmallerThanPreviousObservation.selector);
        vm.startPrank(user);

        Observation[] memory observations = new Observation[](2);
        observations[0] = Observation({
            price: 45000,
            timestamp: 1000
        });
        observations[1] = Observation({
            price: 46500,
            timestamp: 900
        });

        oracle.submitObservations(keccak256("BTCUSD"), observations);

        vm.stopPrank();
    }
}
