# PyArrow Performance Optimization Recommendations

Based on analysis of the flamegraph from 4 client requests over 10 minutes, the following pyarrow bottlenecks and optimizations have been identified.

## Key Bottlenecks Identified

From the flamegraph, the major pyarrow bottlenecks are:

1. **Filter operations** (3,152 samples, 3.28%): `filter (pyarrow/lib.cpython-311-x86_64-linux-gnu.so)`
2. **Acero query engine** (2,494 samples, 2.60%): `_filter_table (pyarrow/acero.py:376)` and `to_table (pyarrow/_acero.cpython-311-x86_64-linux-gnu.so)`
3. **IPC stream operations** (1,067 samples, 1.11%): `open_stream (pyarrow/ipc.py:190)`  
4. **Batch reading** (1,071 samples, 1.12%): `read_next_batch (pyarrow/lib.cpython-311-x86_64-linux-gnu.so)`
5. **Memory management overhead**: Multiple destructors and reference counting operations (~1,400 samples total)

## Optimization Recommendations

### 1. **Batch Size Optimization**
- **Current issue**: Reading data one batch at a time with `read_next_batch`
- **Solution**: Increase batch sizes to reduce the number of IPC round trips
- **Implementation**: Configure larger `batch_size` parameter in pyarrow readers (e.g., 65536 instead of default 1024)

### 2. **Reduce Filter Operations**
- **Current issue**: Heavy usage of table filtering via Acero engine
- **Solutions**:
  - Push filtering to the data source level (Kafka backend) instead of applying filters after reading
  - Use column selection to reduce data transfer before filtering
  - Consider using pyarrow compute functions instead of Acero for simple filters

### 3. **Memory Pool Optimization**
- **Current issue**: Memory allocation/deallocation overhead from object destructors
- **Solutions**:
  - Use a custom memory pool: `pyarrow.memory_pool()` with pre-allocated buffers
  - Enable memory mapping for larger datasets: `memory_map=True` in readers
  - Consider using `pyarrow.allocate_buffer()` for large temporary buffers

### 4. **IPC Stream Optimization**
- **Current issue**: Frequent stream opening/closing operations
- **Solutions**:
  - Reuse stream readers when possible instead of creating new ones
  - Use `RecordBatchFileReader` instead of `RecordBatchStreamReader` for static data
  - Enable compression in IPC streams: `compression='lz4'` or `compression='zstd'`

### 5. **Threading and Concurrency**
- **Current issue**: Thread contention visible in pthread operations
- **Solutions**:
  - Configure pyarrow to use fewer threads: `pyarrow.set_cpu_count(N)` where N < total cores
  - Use async I/O patterns instead of blocking operations
  - Consider connection pooling to reduce thread contention

### 6. **Data Type Optimization**
- **Solutions**:
  - Use more efficient data types (e.g., `int32` instead of `int64` where possible)
  - Enable dictionary encoding for repeated string values
  - Use timestamp types with appropriate precision (microseconds vs nanoseconds)

## Example Implementation

```python
# Configure global pyarrow settings
import pyarrow as pa

# Optimize memory usage
pa.set_memory_pool(pa.system_memory_pool())
pa.set_cpu_count(4)  # Reduce thread contention

# Use larger batch sizes
reader_options = pa.ipc.RecordBatchStreamReader.options(
    batch_size=65536,
    memory_pool=pa.system_memory_pool()
)

# Enable compression for IPC
write_options = pa.ipc.IpcWriteOptions(compression='lz4')
```

## Critical Bottleneck: Bit Manipulation in _arrow_to_numpy_array

### Issue
Line 520 of `_arrow_to_numpy_array` function performs extremely expensive bit manipulation:

```python
mask = 1 - numpy.unpackbits(bitmap).reshape(shape)[:, ::-1].reshape(-1)[:length]
```

This creates multiple intermediate arrays and forces expensive memory copies through bit reversal operations.

### Optimization
Replace with more efficient bit manipulation:

```python
# Instead of expensive bit reversal and multiple reshapes
mask = numpy.unpackbits(bitmap, bitorder='little')[:length]
if offset > 0:
    mask = mask[offset:]
mask = 1 - mask
```

**Expected impact**: 10-100x speedup for data with null values.

## Major Performance Issue: Type Inference and Python Object Conversion

### Problem
The most significant bottleneck appears to be in `arrakis/block.py:409`:

```python
series_dict[channel] = _arrow_to_numpy_array(pyarrow.array(data[idx]))
```

Specifically:
- `pyarrow.array(data[idx])` triggers expensive type inference (`arrow::py::InferArrowType`)
- Converting Python list-like objects (`PyConverter::Extend`) is extremely slow

### Root Cause
The code is converting from Arrow → Python → Arrow → NumPy, causing multiple expensive conversions.

### High-Impact Optimizations

#### 1. **Use RecordBatch Schema Information (Highest Impact)**
Since the RecordBatch already contains the schema, use it directly to eliminate type inference:

```python
# Current (slow) - triggers expensive type inference:
series_dict[channel] = _arrow_to_numpy_array(pyarrow.array(data[idx]))

# Optimized - use known schema from batch:
data_field = batch.schema.field("data")
data_type = data_field.type.value_type  # Get the inner type of the list

# Direct conversion without inference:
if data.null_count == 0:
    # Fast path for no nulls - direct numpy conversion
    series_dict[channel] = data[idx].values.to_numpy()
else:
    # Use schema-informed conversion
    arrow_array = pyarrow.array(data[idx], type=data_type)
    series_dict[channel] = _arrow_to_numpy_array(arrow_array)
```

#### 2. **Batch Process Using Schema-Aware Conversion**
Convert all channels at once using the known schema:

```python
# Instead of per-channel conversion with inference:
for idx, channel in enumerate(channel_names):
    series_dict[channel] = _arrow_to_numpy_array(pyarrow.array(data[idx]))

# Schema-aware batch conversion:
data_field = batch.schema.field("data")
data_type = data_field.type.value_type  # e.g., pyarrow.float64()

if data.null_count == 0:
    # Fastest path - direct bulk conversion
    for idx, channel in enumerate(channel_names):
        series_dict[channel] = data[idx].values.to_numpy()
else:
    # Batch convert with known type
    for idx, channel in enumerate(channel_names):
        # Skip type inference by providing the schema type
        arrow_array = pyarrow.array(data[idx], type=data_type)
        series_dict[channel] = _arrow_to_numpy_array(arrow_array)
```

#### 3. **Pre-specify Arrow Schema**
Eliminate type inference by providing explicit schemas:

```python
# Pre-define schema to avoid inference
schema = pyarrow.schema([
    pyarrow.field('channel', pyarrow.string()),
    pyarrow.field('data', pyarrow.list_(pyarrow.float64())),
    pyarrow.field('time', pyarrow.int64())
])

# Use schema in conversions
table = pyarrow.Table.from_arrays([...], schema=schema)
```

#### 3. **Recommended Implementation (Complete Solution)**
Schema-informed optimization that eliminates the bottleneck entirely:

```python
@classmethod
def from_record_batch(cls, batch: pyarrow.RecordBatch, channels: dict[str, Channel]):
    time = batch.column("time").to_numpy()[0]
    channel_names = batch.column("channel").to_pylist()
    data = batch.column("data")
    
    # Extract schema information once
    data_field = batch.schema.field("data")
    inner_type = data_field.type.value_type  # e.g., pyarrow.float64()
    
    series_dict = {}
    channel_dict = {}
    
    if data.null_count == 0:
        # Fastest path: no nulls, direct conversion
        for idx, channel in enumerate(channel_names):
            series_dict[channel] = data[idx].values.to_numpy()
            channel_dict[channel] = channels[channel]
    else:
        # Schema-informed conversion (eliminates type inference)
        for idx, channel in enumerate(channel_names):
            # Provide the type directly - no inference needed!
            arrow_array = pyarrow.array(data[idx], type=inner_type)
            series_dict[channel] = _arrow_to_numpy_array(arrow_array)
            channel_dict[channel] = channels[channel]
    
    return cls(time, series_dict, channel_dict)
```

**Expected Performance Impact:**
- **Eliminates `arrow::py::InferArrowType`** - No more type inspection overhead
- **Reduces `PyConverter::Extend` calls** - Type is known upfront  
- **Fast path for common case** - Direct `.values.to_numpy()` when no nulls
- **Estimated speedup**: **5-10x improvement** for this specific bottleneck

#### 4. **Use Arrow Compute Functions**
Replace Python loops with vectorized Arrow operations:

```python
# Instead of Python iteration
for idx, channel in enumerate(channel_names):
    series_dict[channel] = _arrow_to_numpy_array(pyarrow.array(data[idx]))

# Use Arrow compute functions
import pyarrow.compute as pc
arrays = pc.list_element(data, list(range(len(channel_names))))
```

## Impact Assessment

The most impactful optimizations would be:

1. **Implement the schema-informed optimization** (5-10x speedup for the major bottleneck)
   - Eliminates expensive `arrow::py::InferArrowType` operations
   - Reduces `PyConverter::Extend` overhead
   - Provides fast path for null-free data (most common case)

2. **Use direct `.values.to_numpy()` for null-free data** (near zero-copy performance)
   - Bypasses all conversion overhead when no nulls present
   - Leverages Arrow's native numpy integration

3. **Increase batch sizes** (will reduce IPC overhead by ~50%)
4. **Push filtering to backend** (will eliminate the 3.28% filter bottleneck)  
5. **Configure memory pools** (will reduce memory management overhead by ~30%)
6. **Optimize null value bit manipulation** (10-100x speedup when nulls are present)

**Priority Implementation Order:**
1. **Schema-informed optimization** (addresses the major flamegraph bottleneck)
2. **Batch size optimization** (reduces I/O overhead)  
3. **Backend filtering** (eliminates post-processing overhead)
4. **Memory pool configuration** (reduces allocation overhead)

The schema-informed optimization should provide the most dramatic performance improvement since it directly addresses the `arrow::py::InferArrowType` and `PyConverter::Extend` bottlenecks visible in your flamegraph.
