# Arrakis Server Scaling Analysis & Optimizations

## Performance Summary

### Current Scaling Characteristics
- **20 clients**: Well-optimized, minimal bottlenecks
- **40 clients**: Manageable but showing stress patterns  
- **60 clients**: Server falls behind, cannot keep up

### Previous Successful Optimizations
- ✅ **Arrow type inference elimination**: Schema-informed operations
- ✅ **Threading contention reduction**: `pyarrow.set_cpu_count(1)`
- ✅ **Acero query overhead elimination**: Direct compute filtering
- ✅ **NumPy conversion optimization**: `to_numpy()` → `as_py()`

## Flamegraph Analysis: 20 vs 40 Clients

### Scaling Pattern Analysis

**Linear Scaling (Good):**
- **Kafka consumption**: 42.73% → 37.84% (handled load increase well)
- Consumer wait time scaled appropriately with client count

**Super-Linear Scaling (Scaling Killers):**
- **Arrow memory management**: 5.19% → 7.21% (39% worse per client)
- **Object deallocation overhead** growing faster than client count
- **Threading contention** patterns intensifying

### Root Cause: Why 60 Clients Fail

1. **Memory Pressure Explosion**: Arrow `RecordBatchReader` deallocation overhead is the primary scaling killer
2. **Kafka Consumer Near Saturation**: At 40 clients spending ~38% time waiting; 60 would exceed sustainable limits
3. **GIL/Threading Contention**: Lock wait patterns and futex contention increasing

## Proposed Optimizations

### 1. Arrow Buffer Recycling (HIGH PRIORITY)

**Problem**: Arrow object deallocation takes 7.21% at 40 clients vs 5.19% at 20 clients - growing super-linearly

**Solution**: Implement object pools to reuse Arrow objects instead of creating/destroying them

```python
# In Connection.__init__():
from collections import deque
self._batch_pool = deque(maxlen=50)      # Pool for reusing RecordBatch objects  
self._reader_pool = deque(maxlen=20)     # Pool for IPC readers

# Usage in hot loop:
def get_pooled_reader(self, stream_data):
    """Get reader from pool or create new one"""
    try:
        reader = self._reader_pool.popleft()
        # Reset/reinitialize reader with new stream data
        return reader
    except IndexError:
        # Pool empty, create new reader
        return pyarrow.ipc.open_stream(stream_data)

def return_pooled_reader(self, reader):
    """Return reader to pool for reuse"""
    # Clean up reader state
    self._reader_pool.append(reader)
```

**Expected Impact**: Reduce 7.21% → ~3-4% (back to 20-client levels)

**Implementation Details Needed**:
- How to properly reset/reinitialize pooled IPC readers
- Lifecycle management for pooled RecordBatch objects
- Thread safety for pool access

### 2. Kafka Consumer Connection Pooling (MEDIUM PRIORITY)

**Problem**: Each client connection creates individual Kafka consumers, leading to resource contention at scale

**Current Architecture**:
```python
# Each Connection instance creates its own Consumer
self._consumer = Consumer(consumer_settings)  # 40 consumers for 40 clients
```

**Proposed Architecture**:
```python
# Shared consumer pool across connections
class KafkaConsumerPool:
    def __init__(self, server, pool_size=10):
        self._consumers = Queue(maxsize=pool_size)
        # Pre-create optimized number of consumers
        
    def get_consumer(self):
        """Get consumer from pool"""
        return self._consumers.get()
        
    def return_consumer(self, consumer):
        """Return consumer to pool"""
        self._consumers.put(consumer)

# In Connection class:
def __init__(self, server, partitions, channels, consumer_pool):
    self._consumer_pool = consumer_pool  # Shared pool instead of individual consumer
```

**Expected Impact**: Reduce Kafka wait from 37.84% → ~25-30%

**Concerns & Questions**:
- **Message ordering**: How does pooling affect per-partition message ordering guarantees?
- **Consumer group management**: Impact on Kafka consumer group rebalancing
- **Connection lifecycle**: How to handle consumer cleanup when clients disconnect
- **Thread safety**: Ensuring safe consumer sharing across threads

### 3. Batch Processing (REJECTED)

**Reason**: Cannot accept latency increase for throughput improvement. Real-time timeseries serving requires low latency.

## Implementation Priority

### Phase 1: Arrow Buffer Recycling
- **Risk**: Low - primarily internal optimization
- **Impact**: High - addresses primary scaling bottleneck
- **Complexity**: Medium - requires careful object lifecycle management

### Phase 2: Consumer Pooling Analysis
- **Risk**: Medium - could affect message delivery guarantees  
- **Impact**: High - addresses secondary scaling bottleneck
- **Complexity**: High - significant architectural change

## Alternative Scaling Approaches

If the above optimizations insufficient for >60 clients:

1. **Async I/O Architecture**: Replace threading with asyncio (major rewrite)
2. **Horizontal Scaling**: Multiple server instances with load balancing
3. **Producer-side Filtering**: Move filtering logic to Kafka producers
4. **Streaming Response Architecture**: Replace batch responses with streaming

## Success Metrics

**Target**: Handle 60+ concurrent clients without falling behind

**Key Performance Indicators**:
- Arrow deallocation overhead: <4% (down from 7.21%)
- Kafka consumer wait time: <30% (down from 37.84%) 
- Memory usage growth: Linear with client count (not super-linear)
- No threading contention patterns in flamegraphs

## Next Steps

1. **Implement Arrow buffer recycling** with detailed usage patterns
2. **Prototype consumer pooling** with careful analysis of message ordering impact  
3. **Profile at 40 clients** to validate improvements
4. **Scale test to 60 clients** to confirm success
5. **Document lessons learned** for future scaling phases

---
*Analysis based on flamegraph profiling with py-spy at 20 and 40 concurrent clients*
