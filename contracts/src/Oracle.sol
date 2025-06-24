pragma solidity >=0.8.9 <=0.8.24;

import {Subcall} from "@oasisprotocol/sapphire-contracts/contracts/Subcall.sol";

// Observations.
struct Observation {
    uint price; // base-10 price. The number of decimals is specific to the trading pair and exchange.
    uint64 timestamp;
}

// Oracle is a price-feed oracle smart contract for a specific exchange.
// It can store price feeds of multiple trading pairs.
contract Oracle {
    // Allow access to a specific ROFL app.
    bytes21 public roflAppID;

    error TimestampSmallerThanPreviousObservation();
    error NoObservationsAvailable();

    modifier roflAppOnly {
        // Ensure only the authorized ROFL app can submit.
        if (roflAppID !=0) {
            Subcall.roflEnsureAuthorizedOrigin(roflAppID);
        }
        _;
    }

    mapping(bytes32 => Observation[]) public _observations;

    constructor(bytes21 _roflAppID) {
        _roflAppID = _roflAppID;
    }

    // submitObservations appends the observations of the given trading pair.
    // The tradingPairHash parameter should be keccak256() of the exchange-specific
    // ticker (e.g. keccak256("BTCUSD")) or the 0x-string represented ERC-20
    // token addresses (e.g. keccak256("0x1234567890abcdef12340x1234567890abcdef1234").
    // The observation price decimals is exchange and trading-pair specific.
    function submitObservations(bytes32 tradingPairHash, Observation[] calldata observations) roflAppOnly external {
        uint64 ts = (_observations[tradingPairHash].length > 0) ? _observations[tradingPairHash][_observations[tradingPairHash].length-1].timestamp : 0;
        for (uint i = 0; i < observations.length; i++) {
            if (observations[i].timestamp < ts) {
                revert TimestampSmallerThanPreviousObservation();
            }
            _observations[tradingPairHash].push(observations[i]);
            ts = observations[i].timestamp;
        }
    }

    // Convenience function to fetch the last observation for the given trading
    // pair (e.g. "BTCUSD",
    // ""0x1234567890abcdef12340x1234567890abcdef1234"").
    function getLastObservation(string calldata tradingPair) external view returns (Observation memory) {
        if (_observations[keccak256(bytes(tradingPair))].length == 0) {
            revert NoObservationsAvailable();
        }

        bytes32 hash = keccak256(bytes(tradingPair));
        return _observations[hash][_observations[hash].length-1];
    }


    function getObservationsLength(string calldata tradingPair) external view returns (uint) {
        if (_observations[keccak256(bytes(tradingPair))].length == 0) {
            revert NoObservationsAvailable();
        }

        return _observations[keccak256(bytes(tradingPair))].length;
    }

    function getObservations(string calldata tradingPair, int page, uint count) external view returns (Observation[] memory) {
        if (_observations[keccak256(bytes(tradingPair))].length == 0) {
            revert NoObservationsAvailable();
        }

        bytes32 hash = keccak256(bytes(tradingPair));

        uint start;
        uint end;

        if (page >= 0) {
            // Normal page.
            start = uint(page) * count;
            end = start + count;

            // Sanity checks.
            if (start > _observations[hash].length) {
                start = _observations[hash].length-1;
            }
            if (end > _observations[hash].length) {
                end = _observations[hash].length;
            }
        } else {
            // Return last page.
            end = _observations[hash].length;
            start = end > count ? end - count : 0;
        }

        Observation[] memory resultPage = new Observation[](end - start);
        for (uint i = start; i < end; i++) {
            resultPage[i-start] = _observations[hash][i];
        }
        return resultPage;
    }
}
