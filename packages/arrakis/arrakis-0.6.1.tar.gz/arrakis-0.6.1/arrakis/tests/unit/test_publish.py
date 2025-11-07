"""Unit tests for Publisher functionality."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock, patch

import pyarrow
import pytest

from arrakis.block import SeriesBlock
from arrakis.channel import Channel
from arrakis.publish import Publisher, serialize_batch


def test_serialize_batch():
    """Test batch serialization."""
    schema = pyarrow.schema(
        [
            pyarrow.field("time", pyarrow.int64()),
            pyarrow.field("data", pyarrow.float64()),
        ]
    )
    batch = pyarrow.RecordBatch.from_arrays(
        [
            pyarrow.array([1000000000, 1000000001]),
            pyarrow.array([1.0, 2.0]),
        ],
        schema=schema,
    )

    serialized = serialize_batch(batch)
    assert isinstance(serialized, pyarrow.Buffer)

    # Verify we can deserialize it back
    reader = pyarrow.ipc.open_stream(serialized)
    deserialized = reader.read_next_batch()
    assert deserialized.equals(batch)


@pytest.fixture
def mock_channels():
    """Create mock channels for testing."""
    return {
        "H1:TEST-CHANNEL_1": Channel(
            name="H1:TEST-CHANNEL_1",
            data_type="float64",
            sample_rate=16384,
            publisher="test_publisher",
            partition_id="partition_1",
            partition_index=1,
        ),
        "H1:TEST-CHANNEL_2": Channel(
            name="H1:TEST-CHANNEL_2",
            data_type="float32",
            sample_rate=512,
            publisher="test_publisher",
            partition_id="partition_2",
            partition_index=2,
        ),
    }


@pytest.fixture
def mock_client():
    """Create a mock Arrakis client."""
    with patch("arrakis.publish.Client") as mock_client_class:
        yield mock_client_class.return_value


@pytest.fixture
def mock_flight_server():
    """Create a mock Flight server for context manager setup."""
    with (
        patch("arrakis.publish.connect") as mock_connect,
        patch("arrakis.publish.MultiEndpointStream") as mock_stream_class,
    ):
        # Setup Flight client mock
        mock_flight_client = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_flight_client

        # Setup flight info mock
        mock_flight_info = MagicMock()
        mock_flight_info.endpoints = ["endpoint1"]
        mock_flight_client.get_flight_info.return_value = mock_flight_info

        # Setup stream mock to return Kafka config
        mock_stream = mock_stream_class.return_value.__enter__.return_value
        mock_stream.unpack.return_value = [
            {
                "properties": [
                    ("bootstrap.servers", "localhost:9092"),
                    ("security.protocol", "PLAINTEXT"),
                ]
            },
        ]

        yield mock_flight_client


@pytest.fixture
def mock_kafka_producer():
    """Create a mock Kafka producer."""
    with patch("mockafka.FakeProducer") as mock_producer_class:
        fake_producer = mock_producer_class.return_value
        with patch("arrakis.publish.Producer", return_value=fake_producer):
            yield fake_producer


@pytest.fixture
def mock_series_block(mock_channels):
    """Create a mock SeriesBlock for testing."""
    block = MagicMock(spec=SeriesBlock)
    block.channels = mock_channels

    # Mock to_row_batches to return test data
    batch1 = pyarrow.RecordBatch.from_arrays(
        [
            pyarrow.array([1000000000]),
            pyarrow.array([1.0]),
        ],
        schema=pyarrow.schema(
            [
                pyarrow.field("time", pyarrow.int64()),
                pyarrow.field("H1:TEST-CHANNEL_1", pyarrow.float64()),
            ]
        ),
    )

    batch2 = pyarrow.RecordBatch.from_arrays(
        [
            pyarrow.array([1000000000]),
            pyarrow.array([2.0], type=pyarrow.float32()),
        ],
        schema=pyarrow.schema(
            [
                pyarrow.field("time", pyarrow.int64()),
                pyarrow.field("H1:TEST-CHANNEL_2", pyarrow.float32()),
            ]
        ),
    )

    # Mock to_row_batches to accept a partitions dict and return appropriate batches
    def mock_to_row_batches(partitions):
        result = []
        for channel_name, partition_info in partitions.items():
            if channel_name == "H1:TEST-CHANNEL_1":
                result.append((partition_info.id, batch1))
            elif channel_name == "H1:TEST-CHANNEL_2":
                result.append((partition_info.id, batch2))
        return result

    block.to_row_batches.side_effect = mock_to_row_batches

    return block


def test_register_success(mock_channels, mock_client):
    """Test successful publisher registration."""
    # Setup the mock client to return test channels
    mock_client.find.return_value = list(mock_channels.values())

    publisher = Publisher("test_publisher", "grpc://localhost:8000")
    result = publisher.register()

    assert result is publisher  # Should return self for chaining
    assert publisher.channels == mock_channels

    # Verify client was called correctly
    mock_client.find.assert_called_once_with(publisher="test_publisher")


def test_register_unknown_publisher(mock_client):
    """Test registration fails for unknown publisher."""
    # Mock the client to return no channels
    mock_client.find.return_value = []

    publisher = Publisher("test_publisher", "grpc://localhost:8000")

    with pytest.raises(ValueError, match="unknown publisher ID 'test_publisher'"):
        publisher.register()


def test_register_channel_without_partition(mock_client):
    """Test registration fails when channel lacks partition_id."""
    # Create channel without partition_id
    channel_no_partition = Channel(
        name="H1:TEST-CHANNEL_NO_PARTITION",
        data_type="float64",
        sample_rate=16384,
        publisher="test_publisher",
        partition_id=None,
    )

    mock_client.find.return_value = [channel_no_partition]

    publisher = Publisher("test_publisher", "grpc://localhost:8000")

    with pytest.raises(
        ValueError, match="could not determine partition_id for channel"
    ):
        publisher.register()


def test_publish_success(
    mock_channels,
    mock_client,
    mock_flight_server,
    mock_kafka_producer,
    mock_series_block,
):
    """Test successful publishing with mock producer."""
    # Setup the mock client to return test channels
    mock_client.find.return_value = list(mock_channels.values())

    # Test full workflow with context manager
    publisher = Publisher("test_publisher", "grpc://localhost:8000")

    with publisher.register():
        # Publish the block
        publisher.publish(mock_series_block)

    # Verify produce was called for each partition
    assert mock_kafka_producer.produce.call_count == 2

    # Check the calls
    calls = mock_kafka_producer.produce.call_args_list

    # First call should be for partition_1
    first_call = calls[0]
    assert first_call[1]["topic"] == "arrakis-partition_1"
    assert "value" in first_call[1]

    # Second call should be for partition_2
    second_call = calls[1]
    assert second_call[1]["topic"] == "arrakis-partition_2"
    assert "value" in second_call[1]

    # Verify flush was called after each produce and during cleanup
    assert mock_kafka_producer.flush.call_count >= 2


def test_publish_without_context_manager(mock_series_block):
    """Test publishing fails when used outside context manager."""
    # Create a publisher but don't use context manager (register + enter)
    publisher = Publisher("test_publisher", "grpc://localhost:8000")

    # Try to publish without proper setup - should raise RuntimeError
    with pytest.raises(RuntimeError, match="publication interface not initialized"):
        publisher.publish(mock_series_block)


def test_publish_not_initialized(mock_channels, mock_client, mock_series_block):
    """Test publishing fails after registration but without entering context manager."""
    # Setup registered publisher but don't enter context manager
    mock_client.find.return_value = list(mock_channels.values())
    publisher = Publisher("test_publisher", "grpc://localhost:8000")
    publisher.register()  # Register but don't enter context manager

    # Try to publish without calling enter() - should raise RuntimeError
    with pytest.raises(RuntimeError, match="publication interface not initialized"):
        publisher.publish(mock_series_block)


def test_publish_unknown_channel(
    mock_channels, mock_client, mock_flight_server, mock_kafka_producer
):
    """Test publishing fails with unknown channel."""
    # Setup registered publisher
    mock_client.find.return_value = list(mock_channels.values())
    publisher = Publisher("test_publisher", "grpc://localhost:8000")

    # Create block with a different channel
    different_channel = Channel(
        name="H1:DIFFERENT-CHANNEL",
        data_type="float64",
        sample_rate=16384,
        publisher="test_publisher",
        partition_id="partition_2",
    )

    block = MagicMock(spec=SeriesBlock)
    block.channels = {"H1:DIFFERENT-CHANNEL": different_channel}

    with publisher.register(), pytest.raises(KeyError):
        publisher.publish(block)


def test_publish_modified_channel(
    mock_channels, mock_client, mock_flight_server, mock_kafka_producer
):
    """Test publishing fails with modified channel metadata."""
    # Setup registered publisher
    mock_client.find.return_value = list(mock_channels.values())
    publisher = Publisher("test_publisher", "grpc://localhost:8000")

    # Create block with same channel name but different metadata
    modified_channel = Channel(
        name="H1:TEST-CHANNEL_1",
        data_type="float32",  # Different data type from registered channel
        sample_rate=16384,
        publisher="test_publisher",
        partition_id="partition_1",
    )

    block = MagicMock(spec=SeriesBlock)
    block.channels = {"H1:TEST-CHANNEL_1": modified_channel}

    with (
        publisher.register(),
        pytest.raises(ValueError, match="invalid channel for this publisher"),
    ):
        publisher.publish(block)


def test_publish_with_timeout(
    mock_channels,
    mock_client,
    mock_flight_server,
    mock_kafka_producer,
    mock_series_block,
):
    """Test publishing with custom timeout."""

    # Setup registered publisher
    mock_client.find.return_value = list(mock_channels.values())
    publisher = Publisher("test_publisher", "grpc://localhost:8000")

    with publisher.register():
        # Publish with custom timeout
        publisher.publish(mock_series_block, timeout=timedelta(seconds=5))

    # Verify produce was still called
    assert mock_kafka_producer.produce.call_count == 2


def test_publish_multiple_blocks(
    mock_channels,
    mock_client,
    mock_flight_server,
    mock_kafka_producer,
    mock_series_block,
):
    """Test publishing multiple blocks in sequence."""
    # Setup registered publisher
    mock_client.find.return_value = list(mock_channels.values())
    publisher = Publisher("test_publisher", "grpc://localhost:8000")

    with publisher.register():
        # Publish multiple blocks
        publisher.publish(mock_series_block)
        publisher.publish(mock_series_block)
        publisher.publish(mock_series_block)

    # Verify produce was called for each block (3 blocks x 2 partitions each)
    assert mock_kafka_producer.produce.call_count == 6
    assert mock_kafka_producer.flush.call_count >= 6


def test_publish_single_channel_block(
    mock_channels, mock_client, mock_flight_server, mock_kafka_producer
):
    """Test publishing a block with only one channel."""
    # Setup registered publisher
    mock_client.find.return_value = list(mock_channels.values())
    publisher = Publisher("test_publisher", "grpc://localhost:8000")

    # Create block with only one channel
    single_channel = {"H1:TEST-CHANNEL_1": mock_channels["H1:TEST-CHANNEL_1"]}

    block = MagicMock(spec=SeriesBlock)
    block.channels = single_channel

    # Mock to_row_batches for single channel
    batch = pyarrow.RecordBatch.from_arrays(
        [
            pyarrow.array([1000000000]),
            pyarrow.array([1.0]),
        ],
        schema=pyarrow.schema(
            [
                pyarrow.field("time", pyarrow.int64()),
                pyarrow.field("H1:TEST-CHANNEL_1", pyarrow.float64()),
            ]
        ),
    )

    block.to_row_batches.return_value = [("partition_1", batch)]

    with publisher.register():
        publisher.publish(block)

    # Verify produce was called only once for single partition
    assert mock_kafka_producer.produce.call_count == 1
    call_args = mock_kafka_producer.produce.call_args_list[0]
    assert call_args[1]["topic"] == "arrakis-partition_1"


def test_publish_with_serialized_data_verification(
    mock_channels,
    mock_client,
    mock_flight_server,
    mock_kafka_producer,
    mock_series_block,
):
    """Test that published data is properly serialized."""
    # Setup registered publisher
    mock_client.find.return_value = list(mock_channels.values())
    publisher = Publisher("test_publisher", "grpc://localhost:8000")

    with publisher.register():
        publisher.publish(mock_series_block)

    # Check that produce was called with serialized data
    calls = mock_kafka_producer.produce.call_args_list
    for call in calls:
        # Each call should have topic and value (serialized data)
        assert "topic" in call[1]
        assert "value" in call[1]
        assert isinstance(call[1]["value"], pyarrow.Buffer)
