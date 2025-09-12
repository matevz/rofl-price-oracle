// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import { AggregatorV3Interface } from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";
import { Subcall } from "@oasisprotocol/sapphire-contracts/contracts/Subcall.sol";

contract SimpleAggregator is AggregatorV3Interface {
    // Configuration.
    string public description;
    uint256 public version;
    uint8 public decimals;
    bytes21 public roflAppID;

    // Observations.
    struct Observation {
        uint80 roundId; // Round or unix timestamp for off-chain pairs.
        int256 answer;
        uint256 startedAt;
        uint256 updatedAt;
    }

    mapping(uint80 => Observation) public observations;
    uint80 public latestRoundId;

    // Checks whether the transaction was signed by the ROFL's app key inside
    // TEE.
    modifier onlyTEE() {
        Subcall.roflEnsureAuthorizedOrigin(roflAppID);
        _;
    }

    constructor(bytes21 _roflAppID) {
        roflAppID = _roflAppID;
    }

    function submitObservation(uint80 _roundId, int256 _answer, uint256 _startedAt, uint256 _updatedAt) external onlyTEE {
        observations[_roundId] = Observation({
            roundId: _roundId,
            answer: _answer,
            startedAt: _startedAt,
            updatedAt: _updatedAt
        });

        if (_roundId > latestRoundId) {
            latestRoundId = _roundId;
        }
    }

    function setDescription(string memory _description) external onlyTEE {
        description = _description;
    }

    function setVersion(uint256 _version) external onlyTEE {
        version = _version;
    }

    function setDecimals(uint8 _decimals) external onlyTEE {
        decimals = _decimals;
    }

    function setRoflAppID(bytes21 _roflAppID) external onlyTEE {
        roflAppID = _roflAppID;
    }

    function getRoundData(uint80 _roundId) external view override returns (uint80 roundId, int256 ans, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound) {
        return (_roundId, observations[latestRoundId].answer, observations[latestRoundId].startedAt, observations[latestRoundId].updatedAt, _roundId);
    }

    function latestRoundData() external view override returns (uint80 roundId, int256 ans, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound) {
        return (latestRoundId, observations[latestRoundId].answer, observations[latestRoundId].startedAt, observations[latestRoundId].updatedAt, latestRoundId);
    }
}
