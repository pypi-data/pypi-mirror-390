import numpy
import pyarrow
import pytest

from ...block import Freq, SeriesBlock, Time, combine_blocks, concatenate_blocks
from ...channel import Channel, PartitionInfo


def create_arrays(channels, duration: int = Time.s // 16):
    arrays = {}
    for channel in channels.values():
        size = duration // (channel.sample_rate * Freq.Hz)
        arrays[channel.name] = numpy.random.randint(256, size=size).astype(
            channel.data_type
        )
    return arrays


def create_masked_arrays(channels, duration: int = Time.s // 16):
    arrays = {}
    for channel in channels.values():
        size = duration // (channel.sample_rate * Freq.Hz)
        data = numpy.random.randint(256, size=size).astype(channel.data_type)
        mask = numpy.random.randint(2, size=size)
        arrays[channel.name] = numpy.ma.array(data, mask=mask)
    return arrays


@pytest.fixture(scope="module")
def channels():
    return {
        "H1:FKE-TEST_CHANNEL1": Channel(
            "H1:FKE-TEST_CHANNEL1",
            data_type=numpy.dtype(numpy.float64),
            sample_rate=128,
            partition_id="A",
            partition_index=3,
        ),
        "H1:FKE-TEST_CHANNEL2": Channel(
            "H1:FKE-TEST_CHANNEL2",
            data_type=numpy.dtype(numpy.int32),
            sample_rate=32,
            partition_id="B",
            partition_index=5,
        ),
    }


@pytest.fixture(scope="module")
def arrays(channels, duration: int = Time.s // 16):
    return create_arrays(channels, duration=duration)


@pytest.fixture(scope="module")
def block_nogaps(
    channels, time: int = 1187000000 * Time.s, duration: int = Time.s // 16
):
    arrs = create_arrays(channels, duration)
    return SeriesBlock(time, arrs, channels)


@pytest.fixture(scope="module")
def block_gaps(channels, time: int = 1187000000 * Time.s, duration: int = Time.s // 16):
    arrs = create_masked_arrays(channels, duration)
    return SeriesBlock(time, arrs, channels)


@pytest.mark.parametrize("arrays", [(Time.s // 16)], indirect=["arrays"])
def test_block_creation(channels, arrays):
    time_ns = 1187000000 * Time.s
    duration_ns = Time.s // 16
    block = SeriesBlock(time_ns, arrays, channels)

    # cross-check against expected API
    assert block.time_ns == time_ns
    assert block.duration_ns == duration_ns
    for channel, series in block.items():
        assert series.time_ns == time_ns
        assert series.duration_ns == duration_ns
        assert series.data_type == channels[channel].data_type
        assert series.sample_rate == channels[channel].sample_rate
        assert numpy.array_equal(series.data, arrays[channel])


@pytest.mark.parametrize("block_fixture", ["block_nogaps", "block_gaps"])
def test_column_batch_round_trip(block_fixture, request):
    block = request.getfixturevalue(block_fixture)
    batch = block.to_column_batch()
    rt_block = SeriesBlock.from_column_batch(batch, block.channels)
    assert block.time_ns == rt_block.time_ns
    assert block.duration_ns == rt_block.duration_ns
    assert block.channels == rt_block.channels
    for series, rt_series in zip(block.values(), rt_block.values()):
        assert series.time_ns == rt_series.time_ns
        assert series.duration_ns == rt_series.duration_ns
        assert series.channel == rt_series.channel
        assert numpy.ma.allequal(series.data, rt_series.data)


@pytest.mark.parametrize("block_fixture", ["block_nogaps", "block_gaps"])
def test_column_batch_schema_round_trip(block_fixture, request):
    block = request.getfixturevalue(block_fixture)

    # reverse channels in schema
    original_schema = block._generate_column_schema()  # noqa: SLF001
    time_field = original_schema.field(0)  # time field is always first
    channel_fields = [original_schema.field(i) for i in range(1, len(original_schema))]
    reversed_channel_fields = list(reversed(channel_fields))
    schema = pyarrow.schema([time_field, *reversed_channel_fields])

    batch = block.to_column_batch(schema)
    rt_block = SeriesBlock.from_column_batch(batch, block.channels)
    assert block.time_ns == rt_block.time_ns
    assert block.duration_ns == rt_block.duration_ns
    assert block.channels == rt_block.channels
    for channel_name in block.channels:
        orig_series = block[channel_name]
        rt_series = rt_block[channel_name]
        assert orig_series.time_ns == rt_series.time_ns
        assert orig_series.duration_ns == rt_series.duration_ns
        assert orig_series.channel == rt_series.channel
        assert numpy.ma.allequal(orig_series.data, rt_series.data)


@pytest.mark.parametrize("block_fixture", ["block_nogaps", "block_gaps"])
def test_row_batch_round_trip(block_fixture, request):
    block = request.getfixturevalue(block_fixture)
    partitions = {
        name: PartitionInfo.from_channel(channel)
        for name, channel in block.channels.items()
    }
    index_channel_map = {
        channel.partition_index: channel for channel in block.channels.values()
    }
    (_, batch1), (_, batch2) = block.to_row_batches(partitions)
    block1 = SeriesBlock.from_row_batch(batch1, index_channel_map)
    block2 = SeriesBlock.from_row_batch(batch2, index_channel_map)
    rt_block = combine_blocks(block1, block2)

    assert block.time_ns == rt_block.time_ns
    assert block.duration_ns == rt_block.duration_ns
    assert block.channels == rt_block.channels
    for series, rt_series in zip(block.values(), rt_block.values()):
        assert series.time_ns == rt_series.time_ns
        assert series.duration_ns == rt_series.duration_ns
        assert series.channel == rt_series.channel
        assert numpy.ma.allequal(series.data, rt_series.data)


@pytest.mark.parametrize("arrays", [(Time.s // 16)], indirect=["arrays"])
def test_concatenate_blocks(channels, arrays):
    blocks = []
    start_ns = 1187000000 * Time.s
    end_ns = start_ns + 2 * Time.s
    duration_ns = Time.s // 16

    for time_ns in range(start_ns, end_ns, duration_ns):
        block = SeriesBlock(time_ns, arrays, channels)
        blocks.append(block)

    block = concatenate_blocks(*blocks)
    assert block.time_ns == start_ns
    assert block.duration_ns == (end_ns - start_ns)
    assert block.channels == channels
