# Changelog

## [Unreleased]

## [0.6.1] - 2025-11-06

### Fixed

- Fix issues with publication with partition index scheme
  * Extract partition ID as well for relevant publishing info
  * Fix validation check in partition index for registration
- Extract partition index from metadata in Client, fixes issue where
  find/describe had missing partition index
- Raise correct RuntimeError instead of unclear AttributeError when publishing
  without context manager

## [0.6.0] - 2025-10-28

### Added

- Add `partition_index` attribute to Channel class

### Changed

- Change allowable channel name structure: `<domain>:<subsystem>[-_]<rest>`
  * This allows VIRGO-like channels to be parsed correctly
  * Also expose subsystem property to Channel class
- Update publisher to push channel partition index values instead of names,
  reducing packet sizes
  * Track channel name to ID values during registration and partitioning
  * `SeriesBlock.from_row_batch` takes a partition index - channel map instead

## [0.5.0] - 2025-09-26

### Added

- Allow a pre-defined schema to be passed into `SeriesBlock.to_column_batch`

### Fixed

- Address muxer edge cases causing stale data to not be returned
- Fix edge case in muxer when we get complete data for a newer timestamp after
  incomplete data from an older timestamp

### Changed

- Improve performance of SeriesBlock generation from record batches:
  * Make fath path quicker for non-null Arrow arrays in converting to numpy
    arrays
  * Avoid unnecessary Arrow array type inference
  * Extract single time from batch instead of converting to numpy array first
  * Switch to more efficient bit manipulation to calculate Arrow array mask
    for numpy conversion
- Improve performance of conversion from numpy masked arrays to Arrow arrays
  for nested types

## [0.4.1] - 2025-07-10

### Fixed

- Fix edge case in muxer where multiple blocks with the same time could be
  returned

## [0.4.0] - 2025-06-25

### Added

- Add support for gaps in data, represented as masked arrays in SeriesBlock
- Add property in Series that reports gaps in data
- Allow printing channel as JSON from CLI in arrakis describe/find
- Add --latency option to print buffer latency to stderr
- Add 'expected latency' metadata in Channel
- Allow creation of gaps within SeriesBlock to support server-side gap handling

### Fixed

- Fix match parsing on drop in muxer
- Fix issue where items in muxer when setting `on_drop` to 'warn' was not
  dropping items

## [0.3.0] - 2025-04-16

### Added

- Add option to specify URL in arrakis CLI
- Add dtype alias to `data_type` in Channel
- Add publish sub-command in Arrakis CLI to generate arbitrary streams to
  publish to the specified channels
- Add schema validation to request descriptors for client and server-side
  validation

### Fixed

- Add `min_rate`/`max_rate` arguments if not specified in client, addressing a
  failure if specified as None
- Fix issue in excessive CPU usage when polling MultiEndpointStream
- Coerce data types to strings within Client so they are JSON-serializable
- Fix describe command in arrakis CLI to properly extract channel info for
  display

### Changed

- Use GPSTimeParseAction for time arguments/options in arrakis CLI, allowing
  arbitrary date/time strings
- Redefine __eq__ for Channel, relaxing strict equality for optional fields
- Update publication interface:
  * take the `publisher_id` at initialization, not during register
  * the register step now retrieves the channel list and updates the partition
    info
  * context manager now handles retrieving kafka info from the server to
    allow publication
  * publish method checks consistency of channels being published
- Check channels when initializing publisher

## [0.2.0] - 2025-03-11

### Added

- Add publisher metadata to Channel
- Allow multiple data types in find/count requests
- Allow querying by publisher in find/count requests
- Add `from_json` constructor in Channel
- Add arrakis entry point

### Fixed

- Fix issue in parsing response in Publisher registration
- Improve error handling and mitigate timeouts in MultiEndpointStream polling
- Remove initial describe call within stream endpoint

### Changed

- Allow Channel to handle raw numpy dtypes
- Expose domain property for Channel
- Publisher now only requires a `publisher_id` for registration

### Removed

## [0.1.0] - 2024-11-13

- Initial release.

[unreleased]: https://git.ligo.org/ngdd/arrakis-python/-/compare/0.6.1...main
[0.6.0]: https://git.ligo.org/ngdd/arrakis-python/-/tags/0.6.1
[0.6.0]: https://git.ligo.org/ngdd/arrakis-python/-/tags/0.6.0
[0.5.0]: https://git.ligo.org/ngdd/arrakis-python/-/tags/0.5.0
[0.4.1]: https://git.ligo.org/ngdd/arrakis-python/-/tags/0.4.1
[0.4.0]: https://git.ligo.org/ngdd/arrakis-python/-/tags/0.4.0
[0.3.0]: https://git.ligo.org/ngdd/arrakis-python/-/tags/0.3.0
[0.2.0]: https://git.ligo.org/ngdd/arrakis-python/-/tags/0.2.0
[0.1.0]: https://git.ligo.org/ngdd/arrakis-python/-/tags/0.1.0
