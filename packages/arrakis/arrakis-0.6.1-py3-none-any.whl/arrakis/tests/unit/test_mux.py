from datetime import timedelta

import gpstime
import pytest

from ...block import Time
from ...mux import Muxer


def test_muxer():
    keys = {"A", "B", "C"}
    items = [
        (1, "A", None),
        (2, "A", None),
        (1, "B", None),
        (1, "C", None),
        (2, "B", None),
        (3, "A", None),
        (2, "C", None),
        (3, "C", None),
        (3, "B", None),
    ]

    muxer: Muxer = Muxer(keys)
    for time, key, data in items:
        muxer.push(time, key, data)

    for time, item in enumerate(muxer.pull(), start=1):
        assert item.time == time
        assert set(item.keys()) == keys


def test_muxer_memory_leak_scenario(freezer):
    """Test the memory leak scenario where partial data gets stuck."""
    keys = {"A", "B", "C"}
    timeout = timedelta(seconds=1.0)
    gps_start = 1400000000.0

    freezer.move_to(gpstime.gpstime.fromgps(gps_start))
    muxer: Muxer = Muxer(keys, timeout=timeout)

    # Push partial data for T1
    test_time_1 = int(gps_start * Time.SECONDS)
    muxer.push(test_time_1, "A", "data_A")
    muxer.push(test_time_1, "B", "data_B")
    # Missing "C" for T1

    # Push complete data for T2 (later timestamp)
    test_time_2 = int((gps_start + 10) * Time.SECONDS)
    for key in keys:
        muxer.push(test_time_2, key, f"data_{key}")

    # Pull should yield both T1 (partial, stale) and T2 (complete)
    # The fix means T1 is no longer stuck - it gets yielded as stale partial data
    results = list(muxer.pull())
    assert len(results) == 2
    assert results[0].time == test_time_1  # T1 comes first (older)
    assert results[1].time == test_time_2  # T2 comes second

    # Try to push missing piece for T1 - should be "too old"
    with pytest.warns(UserWarning, match="timestamp is too old"):
        muxer.push(test_time_1, "C", "late_data")

    # Advance time - but T1 was already yielded above, so no new data
    freezer.tick(timeout.total_seconds() + 0.1)

    # No additional data should be yielded (T1 was already returned)
    results = list(muxer.pull())
    assert len(results) == 0


def test_muxer_historical_data_timeout(freezer):
    """Test timeout logic for historical data (all data older than now)."""
    keys = {"A", "B"}
    timeout = timedelta(seconds=1.0)
    gps_start = 1400000000.0

    # Set current time far in future
    gps_now = gps_start + 1000
    freezer.move_to(gpstime.gpstime.fromgps(gps_now))

    muxer: Muxer = Muxer(keys, timeout=timeout, start=int(gps_start * Time.SECONDS))

    # Push partial historical data
    test_time = int(gps_start * Time.SECONDS)
    muxer.push(test_time, "A", "historical_data")
    # Missing "B"

    # move 10 seconds forward (past timeout). historical data should now be 'stale'
    freezer.tick(timeout.total_seconds() + 0.5)

    results = list(muxer.pull())
    assert len(results) == 1
    assert results[0].time == test_time
    assert set(results[0].keys()) == {"A"}


def test_muxer_live_data_timeout(monkeypatch):
    """Test timeout logic for live data (data around current time with latency)."""
    # FIXME: gpstime.gpsnow() is not compatible with freezegun because it uses
    # a direct reference to datetime.datetime.utcnow() that freezegun doesn't patch.
    # This should be fixed upstream in gpstime to be compatible with time mocking.

    keys = {"A", "B"}
    timeout = timedelta(seconds=1.0)
    gps_start = 1400000000.0

    # Mock gpstime.gpsnow to return controlled values
    def mock_gpsnow():
        return gps_start

    monkeypatch.setattr("gpstime.gpsnow", mock_gpsnow)

    # Create muxer with mocked GPS time
    muxer: Muxer = Muxer(keys, timeout=timeout)

    # Push partial live data at the same time as "now"
    test_time = int(gps_start * Time.SECONDS)
    muxer.push(test_time, "A", "live_data")
    # Missing "B"

    # Should not yield immediately (live data, not stale yet)
    results = list(muxer.pull())
    assert len(results) == 0

    # Advance mock time past timeout
    def mock_gpsnow_later():
        return gps_start + timeout.total_seconds() + 0.5

    monkeypatch.setattr("gpstime.gpsnow", mock_gpsnow_later)

    # Now should yield partial data (timed out)
    results = list(muxer.pull())
    assert len(results) == 1
    assert results[0].time == test_time
    assert set(results[0].keys()) == {"A"}


def test_muxer_high_load_memory_accumulation(monkeypatch):
    """Test memory accumulation under high-load conditions with partial timestamps."""
    keys = {"A", "B", "C", "D"}  # More keys = more opportunities for partial data
    timeout = timedelta(seconds=1.0)
    gps_start = 1400000000.0

    # Mock GPS time that advances slowly
    current_gps_time = gps_start

    def mock_gpsnow():
        return current_gps_time

    monkeypatch.setattr("gpstime.gpsnow", mock_gpsnow)

    muxer: Muxer = Muxer(keys, timeout=timeout)

    # Simulate high load: create many timestamps with partial data
    # This simulates what happens when clients send data out of sync under load
    num_timestamps = 50
    for i in range(num_timestamps):
        timestamp = int((gps_start + i * 0.1) * Time.SECONDS)  # 100ms intervals

        # Randomly make some timestamps incomplete (missing 1-2 keys)
        available_keys = list(keys)
        if i % 3 == 0:  # Every 3rd timestamp missing 1 key
            available_keys.remove("D")
        elif i % 7 == 0:  # Every 7th timestamp missing 2 keys
            available_keys.remove("C")
            available_keys.remove("D")

        # Push available data
        for key in available_keys:
            muxer.push(timestamp, key, f"data_{key}_{i}")

    # Check how much data is stuck before timeout
    results_before_timeout = list(muxer.pull())
    complete_before = len(results_before_timeout)

    # Advance time past all timeouts
    current_gps_time = gps_start + num_timestamps * 0.1 + timeout.total_seconds() + 1

    # All remaining partial data should now be yielded
    results_after_timeout = list(muxer.pull())
    partial_after = len(results_after_timeout)

    total_yielded = complete_before + partial_after

    # We should get back all timestamps (some complete, some partial)
    assert total_yielded == num_timestamps, (
        f"Expected {num_timestamps}, got {total_yielded}"
    )

    # Verify muxer internal state is clean
    assert len(muxer._times) == 0, (
        f"Expected empty _times, got {len(muxer._times)} items"
    )
    assert len(muxer._items) == 0, (
        f"Expected empty _items, got {len(muxer._items)} items"
    )


def test_muxer_rapid_late_arrivals(monkeypatch):
    """Test scenario where late arrivals keep triggering the 'too old' path."""
    keys = {"A", "B"}
    timeout = timedelta(seconds=0.1)  # Short timeout to make things happen faster
    gps_start = 1400000000.0

    current_gps_time = gps_start

    def mock_gpsnow():
        return current_gps_time

    monkeypatch.setattr("gpstime.gpsnow", mock_gpsnow)

    muxer: Muxer = Muxer(keys, timeout=timeout)

    # Push data for timestamp T1
    test_time_1 = int(gps_start * Time.SECONDS)
    muxer.push(test_time_1, "A", "data_A_1")

    # Advance time so T1 becomes the new _last_time when pulled
    current_gps_time = gps_start + timeout.total_seconds() + 0.1
    results = list(muxer.pull())
    assert len(results) == 1  # T1 partial data

    # Now simulate rapid late arrivals for T1 that will be "too old"
    # This could cause accumulation if the "too old" path has bugs
    late_arrival_count = 20
    for i in range(late_arrival_count):
        with pytest.warns(UserWarning, match="timestamp is too old"):
            muxer.push(test_time_1, "B", f"late_B_{i}")

    # Push new valid timestamp T2
    test_time_2 = int(current_gps_time * Time.SECONDS)
    muxer.push(test_time_2, "A", "data_A_2")
    muxer.push(test_time_2, "B", "data_B_2")

    # Pull should get T2
    results = list(muxer.pull())
    assert len(results) == 1
    assert results[0].time == test_time_2

    # Muxer should be clean despite all the late arrivals
    assert len(muxer._times) == 0
    assert len(muxer._items) == 0


def test_muxer_overlapping_timeouts(monkeypatch):
    """Test complex scenario with overlapping timeout conditions."""
    keys = {"A", "B", "C"}
    timeout = timedelta(seconds=1.0)
    gps_start = 1400000000.0

    current_gps_time = gps_start

    def mock_gpsnow():
        return current_gps_time

    monkeypatch.setattr("gpstime.gpsnow", mock_gpsnow)

    muxer: Muxer = Muxer(keys, timeout=timeout)

    # Create a complex scenario:
    # - T1: partial data (A, B)
    # - T2: complete data (A, B, C)
    # - T3: partial data (A)
    # - T4: partial data (A, B)
    # - T5: complete data (A, B, C)

    base_time = int(gps_start * Time.SECONDS)

    # T1: partial
    muxer.push(base_time, "A", "data_A_1")
    muxer.push(base_time, "B", "data_B_1")

    # T2: complete
    muxer.push(base_time + Time.SECONDS, "A", "data_A_2")
    muxer.push(base_time + Time.SECONDS, "B", "data_B_2")
    muxer.push(base_time + Time.SECONDS, "C", "data_C_2")

    # T3: partial
    muxer.push(base_time + 2 * Time.SECONDS, "A", "data_A_3")

    # T4: partial
    muxer.push(base_time + 3 * Time.SECONDS, "A", "data_A_4")
    muxer.push(base_time + 3 * Time.SECONDS, "B", "data_B_4")

    # T5: complete
    muxer.push(base_time + 4 * Time.SECONDS, "A", "data_A_5")
    muxer.push(base_time + 4 * Time.SECONDS, "B", "data_B_5")
    muxer.push(base_time + 4 * Time.SECONDS, "C", "data_C_5")

    # With the monotonic timestamp fix, all data gets yielded immediately
    # T1 gets yielded because T2 is complete (monotonic assumption)
    # T3, T4 get yielded because T5 is complete (monotonic assumption)
    # T2, T5 get yielded because they are complete
    results = list(muxer.pull())

    complete_results = [r for r in results if len(r.keys()) == len(keys)]
    partial_results = [r for r in results if len(r.keys()) < len(keys)]

    assert len(complete_results) == 2  # T2 and T5
    assert len(partial_results) == 3  # T1, T3, T4
    assert len(results) == 5  # All timestamps yielded

    # Verify timestamps are in chronological order
    times = [r.time for r in results]
    assert times == sorted(times), "Results should be in chronological order"

    # No additional data should remain after timeout
    current_gps_time = gps_start + 10 + timeout.total_seconds()
    remaining_results = list(muxer.pull())
    assert len(remaining_results) == 0

    # Verify complete cleanup
    assert len(muxer._times) == 0
    assert len(muxer._items) == 0


def test_muxer_burst_traffic_simulation(monkeypatch):
    """Simulate burst traffic patterns that might cause memory issues."""
    keys = {"A", "B", "C"}
    timeout = timedelta(seconds=0.5)
    gps_start = 1400000000.0

    current_gps_time = gps_start

    def mock_gpsnow():
        return current_gps_time

    monkeypatch.setattr("gpstime.gpsnow", mock_gpsnow)

    muxer: Muxer = Muxer(keys, timeout=timeout)

    # Simulate 5 bursts of traffic with gaps between them
    total_timestamps_pushed = 0

    for burst in range(5):
        # Each burst creates 20 timestamps over 0.5 seconds (40 timestamps/sec)
        burst_start_time = gps_start + burst * 2.0  # 2 second gaps between bursts

        for i in range(20):
            # 25ms intervals
            timestamp = int((burst_start_time + i * 0.025) * Time.SECONDS)
            total_timestamps_pushed += 1

            # Make some timestamps incomplete (realistic under high load)
            if i % 4 == 0:  # 25% missing one key
                muxer.push(timestamp, "A", f"data_A_burst{burst}_{i}")
                muxer.push(timestamp, "B", f"data_B_burst{burst}_{i}")
                # Missing C
            elif i % 8 == 0:  # 12.5% missing two keys
                muxer.push(timestamp, "A", f"data_A_burst{burst}_{i}")
                # Missing B, C
            else:  # Most are complete
                for key in keys:
                    muxer.push(timestamp, key, f"data_{key}_burst{burst}_{i}")

        # Advance time through the burst period
        current_gps_time = burst_start_time + 0.5

        # Pull data generated during this burst
        burst_results = list(muxer.pull())

        # Continue to next burst (time gap allows remaining partial data to timeout)
        current_gps_time = burst_start_time + 1.5 + timeout.total_seconds()
        remaining_results = list(muxer.pull())

        print(
            f"Burst {burst}: {len(burst_results)} immediate, "
            f"{len(remaining_results)} after timeout"
        )

    # Final cleanup - advance time way past everything
    current_gps_time = gps_start + 20
    list(muxer.pull())  # Clear any remaining data

    # Verify muxer is completely clean
    assert len(muxer._times) == 0, f"_times not empty: {len(muxer._times)} items remain"
    assert len(muxer._items) == 0, f"_items not empty: {len(muxer._items)} items remain"
