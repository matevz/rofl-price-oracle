// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../src/PriceFeedDirectory.sol";
import {Subcall} from "@oasisprotocol/sapphire-contracts/contracts/Subcall.sol";
import {Test, console} from "forge-std/Test.sol";
import {SapphireTest} from "@oasisprotocol-sapphire-foundry-0.1.1/BaseSapphireTest.sol";

contract PriceFeedDirectoryTest is SapphireTest {
    PriceFeedDirectory public priceFeed;
    SimpleAggregator public simpleAggr;

    function setUp() public override {
        super.setUp();
        bytes21 roflAppId = bytes21(0);
        simpleAggr = new SimpleAggregator(roflAppId);
        priceFeed = new PriceFeedDirectory();
    }

    function test_addFeed() public {
        priceFeed.addFeed("bitstamp.net/btc_usd", simpleAggr, false);
        bytes32 hash = keccak256("000000000000000000000000000000000000000000/bitstamp.net/btc_usd");
        assertEq(address(priceFeed.feeds(hash)), address(simpleAggr), "feed not stored");

        priceFeed.addFeed("binance.com/btc_usd", simpleAggr, true);
        hash = keccak256("000000000000000000000000000000000000000000/binance.com/btc_usd");
        assertEq(address(priceFeed.feeds(hash)), address(simpleAggr), "feed not stored");
        assertEq(address(simpleAggr), address(priceFeed.discoverableFeeds(0)), "feed not discoverable");

        vm.expectRevert();
        priceFeed.addFeed("bitstamp.net/btc_usd", simpleAggr, false);
    }

    function test_submitObservation() public {
        // Test submitting an observation
        uint80 roundId = 100;
        int256 ans = 50000 * 1e8; // $50,000 with 8 decimals
        uint256 started = block.timestamp;
        uint256 updated = block.timestamp+1;

        // Submit observation to the simple aggregator
        simpleAggr.submitObservation(roundId, ans, started, updated);

        // Verify the observation was stored correctly
        (uint80 storedRoundId, int256 storedAns, uint256 storedStarted, uint256 storedUpdated, uint80 storedInRound) = simpleAggr.latestRoundData();
        assertEq(storedRoundId, roundId, "roundId mismatch");
        assertEq(storedAns, ans, "answer mismatch");
        assertEq(storedStarted, started, "started timestamp mismatch");
        assertEq(storedUpdated, updated, "updated timestamp mismatch");

        (storedRoundId, storedAns, storedStarted, storedUpdated, storedInRound) = simpleAggr.getRoundData(roundId);
        assertEq(storedRoundId, roundId, "roundId mismatch");
        assertEq(storedAns, ans, "answer mismatch");
        assertEq(storedStarted, started, "started timestamp mismatch");
        assertEq(storedUpdated, updated, "updated timestamp mismatch");
    }
}
