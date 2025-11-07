# Copyright (c) 2022, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/ngdd/arrakis-python/-/raw/main/LICENSE

"""Publisher API."""

from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING, Literal

import numpy
import pyarrow
from pyarrow.flight import connect

from . import constants
from .channel import PartitionInfo
from .client import Client
from .flight import (
    MultiEndpointStream,
    RequestType,
    RequestValidator,
    create_descriptor,
    parse_url,
)

try:
    from confluent_kafka import Producer
except ImportError:
    HAS_KAFKA = False
else:
    HAS_KAFKA = True

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import timedelta

    from .block import SeriesBlock
    from .channel import Channel


logger = logging.getLogger("arrakis")


def serialize_batch(batch: pyarrow.RecordBatch):
    """Serialize a record batch to bytes.

    Parameters
    ----------
    batch : pyarrow.RecordBatch
        The batch to serialize.

    Returns
    -------
    bytes
        The serialized buffer.

    """
    sink = pyarrow.BufferOutputStream()
    with pyarrow.ipc.new_stream(sink, batch.schema) as writer:
        writer.write_batch(batch)
    return sink.getvalue()


def channel_to_dtype_name(channel: Channel) -> str:
    """Given a channel, return the data type's name."""
    assert isinstance(channel.data_type, numpy.dtype)
    return channel.data_type.name


class Publisher:
    """Publisher to publish timeseries to Arrakis service.

    Parameters
    ----------
    id : str
        Publisher ID string.
    url : str
        Initial Flight URL to connect to.

    """

    def __init__(self, publisher_id: str, url: str | None = None):
        if not HAS_KAFKA:
            msg = (
                "Publishing requires confluent-kafka to be installed."
                "This is provided by the 'publish' extra or it can be "
                "installed manually through pip or conda."
            )
            raise ImportError(msg)

        self.publisher_id = publisher_id
        self.initial_url = parse_url(url)

        self.channels: dict[str, Channel] = {}

        self._producer: Producer
        self._partitions: dict[str, PartitionInfo] = {}
        self._registered = False
        self._validator = RequestValidator()

    def register(self):
        assert not self._registered, "has already registered"

        self.channels = {
            channel.name: channel
            for channel in Client(self.initial_url).find(publisher=self.publisher_id)
        }
        if not self.channels:
            msg = f"unknown publisher ID '{self.publisher_id}'."
            raise ValueError(msg)

        # extract the channel partition map
        self._partitions = {}
        for channel in self.channels.values():
            if not channel.partition_id:
                msg = f"could not determine partition_id for channel {channel}."
                raise ValueError(msg)
            if channel.partition_index is None:
                msg = f"could not determine partition_index for channel {channel}."
                raise ValueError(msg)
            self._partitions[channel.name] = PartitionInfo.from_channel(channel)

        self._registered = True

        return self

    def enter(self):
        if not self._registered:
            msg = "must register publisher interface before publishing."
            raise RuntimeError(msg)

        # get connection properties
        descriptor = create_descriptor(
            RequestType.Publish,
            publisher_id=self.publisher_id,
            validator=self._validator,
        )
        properties: dict[str, str] = {}
        with connect(self.initial_url) as client:
            flight_info = client.get_flight_info(descriptor)
            with MultiEndpointStream(flight_info.endpoints, client) as stream:
                for data in stream.unpack():
                    kv_pairs = data["properties"]
                    properties.update(dict(kv_pairs))

        # set up producer
        self._producer = Producer(
            {
                "message.max.bytes": 10_000_000,  # 10 MB
                "enable.idempotence": True,
                **properties,
            }
        )

    def __enter__(self) -> Publisher:
        self.enter()
        return self

    def publish(
        self,
        block: SeriesBlock,
        timeout: timedelta = constants.DEFAULT_TIMEOUT,
    ) -> None:
        """Publish timeseries data

        Parameters
        ----------
        block : SeriesBlock
            A data block with all channels to publish.
        timeout : timedelta, optional
            The maximum time to wait to publish before timing out.
            Default is 2 seconds.

        """
        if not hasattr(self, "_producer") or not self._producer:
            msg = (
                "publication interface not initialized, "
                "please use context manager when publishing."
            )
            raise RuntimeError(msg)

        for name, channel in block.channels.items():
            if channel != self.channels[name]:
                msg = f"invalid channel for this publisher: {channel}"
                raise ValueError(msg)

        # FIXME: updating partitions should only be allowed for
        # special blessed publishers, that are currently not using
        # this interface, so we're disabling this functionality for
        # the time being, until we have a better way to manage it.
        #
        # # check for new metadata changes
        # changed = set(block.channels.values()) - set(self.channels.values())
        # # exchange to transfer metadata and get new/updated partition IDs
        # if changed:
        #     self._update_partitions(changed)

        # publish data for each data type, splitting into
        # subblocks based on a maximum channel maximum
        for partition_id, batch in block.to_row_batches(self._partitions):
            topic = f"arrakis-{partition_id}"
            logger.debug("publishing to topic %s: %s", topic, batch)
            self._producer.produce(topic=topic, value=serialize_batch(batch))
            self._producer.flush()

    def _update_partitions(
        self, channels: Iterable[Channel]
    ) -> None:  # pragma: no cover
        # set up flight
        assert self._registered, "has not registered yet"
        descriptor = create_descriptor(
            RequestType.Partition,
            publisher_id=self.publisher_id,
            validator=self._validator,
        )
        # FIXME: should we not get FlightInfo first?
        with connect(self.initial_url) as client:
            writer, reader = client.do_exchange(descriptor)

        # send over list of channels to map new/updated partitions for
        dtypes = [channel_to_dtype_name(channel) for channel in channels]
        schema = pyarrow.schema(
            [
                pyarrow.field("channel", pyarrow.string(), nullable=False),
                pyarrow.field("data_type", pyarrow.string(), nullable=False),
                pyarrow.field("sample_rate", pyarrow.int32(), nullable=False),
                pyarrow.field("partition_id", pyarrow.string()),
                pyarrow.field("partition_index", pyarrow.uint32()),
            ]
        )
        batch = pyarrow.RecordBatch.from_arrays(
            [
                pyarrow.array(
                    [str(channel) for channel in channels],
                    type=schema.field("channel").type,
                ),
                pyarrow.array(dtypes, type=schema.field("data_type").type),
                pyarrow.array(
                    [channel.sample_rate for channel in channels],
                    type=schema.field("sample_rate").type,
                ),
                pyarrow.array(
                    [None for _ in channels],
                    type=schema.field("partition_id").type,
                ),
                pyarrow.array(
                    [None for _ in channels],
                    type=schema.field("partition_index").type,
                ),
            ],
            schema=schema,
        )

        # send over the partitions
        writer.begin(schema)
        writer.write_batch(batch)
        writer.done_writing()

        # get back the partition IDs and update
        partitions = reader.read_all().to_pydict()
        for channel, id_, index in zip(
            partitions["channel"],
            partitions["partition_id"],
            partitions["partition_index"],
        ):
            self._partitions[channel] = PartitionInfo(channel, id_, index)

    def close(self) -> None:
        logger.info("closing kafka producer...")
        with contextlib.suppress(Exception):
            self._producer.flush()

    def __exit__(self, *exc) -> Literal[False]:
        self.close()
        return False
