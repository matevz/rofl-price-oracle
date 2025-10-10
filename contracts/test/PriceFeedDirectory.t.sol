// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../src/PriceFeedDirectory.sol";
import {Subcall} from "@oasisprotocol/sapphire-contracts/contracts/Subcall.sol";
import {Test, console} from "forge-std/Test.sol";
import {SapphireTest} from "@oasisprotocol-sapphire-foundry-0.1.2/BaseSapphireTest.sol";

contract PriceFeedDirectoryTest is SapphireTest {
    PriceFeedDirectory public priceFeed;
    SimpleAggregator public simpleAggr;

    function setUp() public override {
        super.setUp();
        bytes21 roflAppId = bytes21(0);
        simpleAggr = new SimpleAggregator(roflAppId);
        priceFeed = new PriceFeedDirectory();
    }

    function test_addFeed_existing_agg() public {
        priceFeed.addFeed("bitstamp.net/btc/usd", simpleAggr, false);
        bytes32 hash = keccak256("000000000000000000000000000000000000000000/bitstamp.net/btc/usd");
        assertEq(address(priceFeed.feeds(hash)), address(simpleAggr), "feed not stored");

        vm.expectRevert();
        priceFeed.addFeed("bitstamp.net/btc/usd", simpleAggr, false);
    }

    function test_addFeed_new_agg() public {
        priceFeed.addFeed("bitstamp.net/btc_usd", RoflAggregatorV3Interface(address(0)), false);
        bytes32 hash = keccak256("000000000000000000000000000000000000000000/bitstamp.net/btc_usd");
        assertNotEq(address(priceFeed.feeds(hash)), address(0), "new feed not deployed");
    }

    function test_addFeed_discoverable() public {
        priceFeed.addFeed("bitstamp.net/btc/usd", simpleAggr, true);
        string memory app_pair = priceFeed.discoverableFeeds(0);
        assertEq(app_pair, "000000000000000000000000000000000000000000/bitstamp.net/btc/usd", "feed not discoverable");
        assertEq(address(simpleAggr), address(priceFeed.feeds(keccak256(bytes(app_pair)))), "discoverable feed not stored");
    }

    function test_submitObservation() public {
        uint80 roundId = 100;
        int256 ans = 50000 * 1e8; // $50,000 with 8 decimals.
        uint256 started = block.timestamp-1;
        uint256 updated = block.timestamp;

        simpleAggr.submitObservation(roundId, ans, started, updated);
        (uint80 storedRoundId, int256 storedAns, uint256 storedStarted, uint256 storedUpdated, uint80 storedInRound) = simpleAggr.latestRoundData();
        assertEq(storedRoundId, roundId, "roundId mismatch");
        assertEq(storedAns, ans, "answer mismatch");
        assertEq(storedStarted, started, "started timestamp mismatch");
        assertEq(storedUpdated, updated, "updated timestamp mismatch");

        (storedRoundId, storedAns, storedStarted, storedUpdated, storedInRound) = simpleAggr.getRoundData(100);
        assertEq(storedRoundId, roundId, "roundId mismatch");
        assertEq(storedAns, ans, "answer mismatch");
        assertEq(storedStarted, started, "started timestamp mismatch");
        assertEq(storedUpdated, updated, "updated timestamp mismatch");

        // Now try a new round.
        uint80 roundId2 = 101;
        int256 ans2 = 60000 * 1e8; // $60,000 with 8 decimals.
        uint256 started2 = block.timestamp+10;
        uint256 updated2 = block.timestamp+11;

        simpleAggr.submitObservation(roundId2, ans2, started2, updated2);
        (storedRoundId, storedAns, storedStarted, storedUpdated, storedInRound) = simpleAggr.latestRoundData();
        assertEq(storedRoundId, roundId2, "roundId mismatch");
        assertEq(storedAns, ans2, "answer mismatch");
        assertEq(storedStarted, started2, "started timestamp mismatch");
        assertEq(storedUpdated, updated2, "updated timestamp mismatch");

        (storedRoundId, storedAns, storedStarted, storedUpdated, storedInRound) = simpleAggr.getRoundData(101);
        assertEq(storedRoundId, roundId2, "roundId mismatch");
        assertEq(storedAns, ans2, "answer mismatch");
        assertEq(storedStarted, started2, "started timestamp mismatch");
        assertEq(storedUpdated, updated2, "updated timestamp mismatch");

        // Test the old round again.
        (storedRoundId, storedAns, storedStarted, storedUpdated, storedInRound) = simpleAggr.getRoundData(100);
        assertEq(storedRoundId, roundId, "roundId mismatch");
        assertEq(storedAns, ans, "answer mismatch");
        assertEq(storedStarted, started, "started timestamp mismatch");
        assertEq(storedUpdated, updated, "updated timestamp mismatch");
    }
}
