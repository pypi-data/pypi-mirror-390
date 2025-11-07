# Changelog

## [Unreleased]

## [0.3.1] - 2025-11-06

### Fixed

- Extract publisher from publisher config filename for use in publisher
  configuration loading

## [0.3.0] - 2025-10-28

### Changed

- When creating cache directory, create parents as needed
- Improved logging of loaded publisher configurations
- Handle reading of incoming record batches that are partition index
  encoded rather than via channel names, reducing data volume
- Require arrakis v0.6+, arrakis-server v0.5+

## [0.2.0] - 2025-09-26

### Added

- Add gaps for missing channels from stream endpoint
- Set timeout in muxer based on maximum latency across channels

### Fixed

- Fix issue with partition endpoint skipping partitioning channels
- Properly handle start/end arguments in stream endpoint:
  * Raises errors when start time contains data that is not available
  * End time being set acts as an termination condition for the stream
- Fix issue where Kafka consumer hangs on assignment when assigning offsets

### Changed

- Do not assign start time if not specified for stream endpoint
- Assign random group IDs for Kafka consumer to avoid sharing consumer offsets
- Switch from appdirs to platformdirs for user cache directory, where metadata
  is stored
- Improve performance for many concurrent clients:
  * Switch to direct compute record batch filtering to reduce overhead
  * Force pyarrow operations to be single-threaded to reduce thread pool contention
  * Extract single time from batch instead of converting to numpy first
  * Optimize arrow IPC stream reader creation/destruction overhead
  * Use a global memory pool for Arrow operations, prioritizing high-performance
    allocators optimized for concurrent workloads
- Increase minimum arrakis-server version to 0.4
- Ignore dropped data going into muxer rather than produce a warning message,
  as this can cause a cascading failure due to logging message overhead

## [0.1.0] - 2025-04-09

- Initial release

[unreleased]: https://git.ligo.org/ngdd/arrakis-backend-kafka/-/compare/0.3.1...main
[0.3.1]: https://git.ligo.org/ngdd/arrakis-backend-kafka/-/tags/0.3.1
[0.3.0]: https://git.ligo.org/ngdd/arrakis-backend-kafka/-/tags/0.3.0
[0.2.0]: https://git.ligo.org/ngdd/arrakis-backend-kafka/-/tags/0.2.0
[0.1.0]: https://git.ligo.org/ngdd/arrakis-backend-kafka/-/tags/0.1.0
