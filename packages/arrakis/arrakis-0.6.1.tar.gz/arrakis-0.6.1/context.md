# Arrakis Server High-Load Memory Issue Investigation

## Current Status: Deep Dive into Muxer Race Condition

### Background
- **Problem**: Server experiences memory growth and "death spiral" at 300+ client loads
- **Original symptom**: "item's timestamp is too old" errors with identical timestamps in logs
- **Example log**: `"item's timestamp is too old: (1438550315000000000 <= 1438550315000000000)"`

### Investigation Progress

#### Phase 1: Initial Fixes Applied ✅
1. **Bit manipulation optimization** in `_arrow_to_numpy_array` - **WORKING**
   - Improved Arrow-to-numpy conversion performance 
   - Allows stable operation at 300 clients initially

2. **Muxer initialization bug fix** - **APPLIED**
   - Changed `_last_time = start` to `_last_time = (start - 1)` 
   - Prevents items at exactly the start time from being rejected

3. **Timeout logic fix** - **APPLIED**  
   - Fixed `_are_items_stale()` calculation for historical vs live data
   - Historical data gets grace period: `oldest_time_allowed = time_now - dt_timeout + dt_lookback`

4. **Monotonic timestamp blocking fix** - **APPLIED**
   - Added `_has_complete_newer_timestamp()` method
   - Prevents complete data from being blocked behind incomplete older data
   - Leverages monotonic timestamp assumption

#### Phase 2: Root Cause Discovery 🎯

**Key Insight**: The muxer behavior is **CORRECT**! The race condition is the real issue.

**Race Condition Identified**:
1. **Partial data arrives** for timestamp T (e.g., keys A, B missing C)
2. **High load causes timeout pressure** → `_are_items_stale(T)` becomes true  
3. **Muxer pulls partial data** for timestamp T → `_last_time` becomes T
4. **Late-arriving data** for timestamp T (key C) gets **correctly rejected** as "too old"
5. **Under high load**: This pattern repeats, creating incomplete data flow

**Test Reproduction**:
```python
def test_muxer_server_scenario_with_timeout_pull():
    # Push partial data for timestamp T
    muxer.push(timestamp, "A", "data_A")  
    
    # Force timeout pull (simulates high load pressure)
    advance_time_past_timeout()
    results = list(muxer.pull())  # _last_time becomes T
    
    # Late arrival gets rejected (CORRECT BEHAVIOR)
    muxer.push(timestamp, "B", "data_B")  # "timestamp is too old" warning
```

### Current Understanding

#### The `<=` Logic is Correct
- `time <= self._last_time` correctly prevents duplicate timestamps from being returned
- Once timestamp T is pulled, no more data should be accepted for T
- The "exactly equal" timestamps in logs are working as designed

#### The Real Problem
- **High load** → **timeout pressure** → **premature pulling of partial data**
- **Memory growth** may be from:
  - Rapid creation/destruction of partial data objects
  - Other system components (not muxer itself)
  - Arrow array allocation patterns under load

#### Missing Test Coverage
- Previous tests used **batch push then pull** patterns
- Real server uses **interleaved push/pull** patterns
- New tests added simulate realistic server behavior

### Next Investigation Steps

#### Option 1: Timeout Tuning
- Investigate if timeout values are appropriate for high-load scenarios
- Consider adaptive timeout based on load conditions
- Profile timeout vs completion rates

#### Option 2: Alternative Memory Sources
- Memory growth might be outside the muxer
- Arrow array allocation/deallocation patterns
- Client connection management
- Other server components under stress

#### Option 3: Backpressure/Flow Control  
- Implement backpressure when muxer is under timeout pressure
- Slow down data ingestion when partial pulls are frequent
- Client-side buffering strategies

### Files Modified
- `arrakis/mux.py`: All timeout and monotonic timestamp fixes
- `arrakis/block.py`: Import fix for Iterable
- `arrakis/tests/unit/test_mux.py`: Comprehensive test suite including race condition reproduction
- `pyproject.toml`: Added SLF001 exception for test file

### Test Cases Added
- `test_muxer_high_load_memory_accumulation`: 50 timestamps with partial data patterns
- `test_muxer_rapid_late_arrivals`: Multiple "too old" rejection scenarios  
- `test_muxer_overlapping_timeouts`: Complex mixed complete/partial scenarios
- `test_muxer_burst_traffic_simulation`: Realistic burst patterns with gaps
- `test_muxer_interleaved_push_pull_live_server_simulation`: Real server behavior simulation
- `test_muxer_server_scenario_with_timeout_pull`: **Race condition reproduction** 

### Key Insight
The muxer is working correctly. The memory issue is likely caused by the **rate** of partial data creation under high load, not by data accumulation within the muxer itself. The race condition creates a pattern where data frequently gets split across multiple incomplete timestamps rather than being efficiently batched.

### Status
- ✅ Muxer logic validated as correct
- ✅ Race condition identified and reproduced  
- 🔍 **Next**: Investigate timeout tuning or alternative memory sources
- 🔍 **Next**: Consider server-level backpressure mechanisms
