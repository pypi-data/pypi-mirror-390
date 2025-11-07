# Copyright (c) 2022, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/ngdd/arrakis-python/-/raw/main/LICENSE

"""Client-based API access."""

import logging
from collections.abc import Generator
from typing import TypeAlias

import numpy
import pyarrow
from pyarrow import flight
from pyarrow.flight import connect

from . import constants
from .block import SeriesBlock, combine_blocks, concatenate_blocks, time_as_ns
from .channel import Channel
from .flight import (
    MultiEndpointStream,
    RequestType,
    RequestValidator,
    create_descriptor,
    parse_url,
)
from .mux import Muxer

logger = logging.getLogger("arrakis")

DataTypeLike: TypeAlias = (
    str | list[str] | type | list[type] | numpy.dtype | list[numpy.dtype]
)


def get_flight_info(
    client: flight.FlightClient, descriptor: flight.FlightDescriptor
) -> flight.FlightInfo:
    flight_info = client.get_flight_info(descriptor)
    logger.debug(
        "flight info received, %g endpoints identified", len(flight_info.endpoints)
    )
    return flight_info


class Client:
    """Client to fetch or publish timeseries.

    Parameters
    ----------
    url : str, optional
        The URL to connect to.
        If the URL is not set, connect to a default server
        or one set by ARRAKIS_SERVER.

    """

    def __init__(self, url: str | None = None):
        self.initial_url = parse_url(url)
        logger.debug("initial url: %s", self.initial_url)
        self._validator = RequestValidator()

    def find(
        self,
        pattern: str = constants.DEFAULT_MATCH,
        data_type: DataTypeLike | None = None,
        min_rate: int | None = constants.MIN_SAMPLE_RATE,
        max_rate: int | None = constants.MAX_SAMPLE_RATE,
        publisher: str | list[str] | None = None,
    ) -> Generator[Channel, None, None]:
        """Find channels matching a set of conditions

        Parameters
        ----------
        pattern : str, optional
            Channel pattern to match channels with, using regular expressions.
        data_type : numpy.dtype-like | list[numpy.dtype-like], optional
            If set, find all channels with these data types.
        min_rate : int, optional
            Minimum sampling rate for channels.
        max_rate : int, optional
            Maximum sampling rate for channels.
        publisher : str | list[str], optional
            If set, find all channels associated with these publishers.

        Yields
        -------
        Channel
            Channel objects for all channels matching query.

        """
        data_type = _parse_data_types(data_type)
        if min_rate is None:
            min_rate = constants.MIN_SAMPLE_RATE
        if max_rate is None:
            max_rate = constants.MAX_SAMPLE_RATE
        if publisher is None:
            publisher = []
        elif isinstance(publisher, str):
            publisher = [publisher]

        descriptor = create_descriptor(
            RequestType.Find,
            pattern=pattern,
            data_type=data_type,
            min_rate=min_rate,
            max_rate=max_rate,
            publisher=publisher,
            validator=self._validator,
        )
        with connect(self.initial_url) as client:
            yield from self._stream_channel_metadata(client, descriptor)

    def count(
        self,
        pattern: str = constants.DEFAULT_MATCH,
        data_type: DataTypeLike | None = None,
        min_rate: int | None = constants.MIN_SAMPLE_RATE,
        max_rate: int | None = constants.MAX_SAMPLE_RATE,
        publisher: str | list[str] | None = None,
    ) -> int:
        """Count channels matching a set of conditions

        Parameters
        ----------
        pattern : str, optional
            Channel pattern to match channels with, using regular expressions.
        data_type : numpy.dtype-like | list[numpy.dtype-like], optional
            If set, find all channels with these data types.
        min_rate : int, optional
            The minimum sampling rate for channels.
        max_rate : int, optional
            The maximum sampling rate for channels.
        publisher : str | list[str], optional
            If set, find all channels associated with these publishers.

        Returns
        -------
        int
            The number of channels matching query.

        """
        data_type = _parse_data_types(data_type)
        if min_rate is None:
            min_rate = constants.MIN_SAMPLE_RATE
        if max_rate is None:
            max_rate = constants.MAX_SAMPLE_RATE
        if publisher is None:
            publisher = []
        elif isinstance(publisher, str):
            publisher = [publisher]

        descriptor = create_descriptor(
            RequestType.Count,
            pattern=pattern,
            data_type=data_type,
            min_rate=min_rate,
            max_rate=max_rate,
            publisher=publisher,
            validator=self._validator,
        )
        count = 0
        with connect(self.initial_url) as client:
            flight_info = get_flight_info(client, descriptor)
            with MultiEndpointStream(flight_info.endpoints, client) as stream:
                for data in stream.unpack():
                    count += data["count"]
        return count

    def describe(self, channels: list[str]) -> dict[str, Channel]:
        """Get channel metadata for channels requested

        Parameters
        ----------
        channels : list[str]
            List of channels to request.

        Returns
        -------
        dict[str, Channel]
            Mapping of channel names to channel metadata.

        """
        descriptor = create_descriptor(
            RequestType.Describe, channels=channels, validator=self._validator
        )
        with connect(self.initial_url) as client:
            return {
                channel.name: channel
                for channel in self._stream_channel_metadata(client, descriptor)
            }

    def stream(
        self,
        channels: list[str],
        start: float | None = None,
        end: float | None = None,
    ) -> Generator[SeriesBlock, None, None]:
        """Stream live or offline timeseries data

        Parameters
        ----------
        channels : list[str]
            List of channels to request.
        start : float, optional
            GPS start time, in seconds.
        end : float, optional
            GPS end time, in seconds.

        Yields
        ------
        SeriesBlock
            Dictionary-like object containing all requested channel data.

        Setting neither start nor end begins a live stream starting
        from now.

        """
        start_ns = time_as_ns(start) if start is not None else None
        end_ns = time_as_ns(end) if end is not None else None
        metadata: dict[str, Channel] = {}
        schemas: dict[str, pyarrow.Schema] = {}

        with connect(self.initial_url) as client:
            descriptor = create_descriptor(
                RequestType.Stream,
                channels=channels,
                start=start_ns,
                end=end_ns,
                validator=self._validator,
            )
            flight_info = get_flight_info(client, descriptor)
            # use the serialized endpoints as the mux keys
            keys = [e.serialize() for e in flight_info.endpoints]
            mux: Muxer = Muxer(keys=keys)
            with MultiEndpointStream(flight_info.endpoints, client) as stream:
                for chunk, endpoint in stream:
                    time = chunk.data.column("time").to_numpy()[0]
                    mux.push(time, endpoint.serialize(), chunk.data)
                    # FIXME: how do we handle stream drop-outs that result
                    # in timeouts in the muxer that result in null data in
                    # the mux pull?
                    for mux_data in mux.pull():
                        blocks = []
                        # update channel metadata if needed
                        for key, batch in mux_data.items():
                            if (
                                key not in schemas
                                or schemas[key].metadata != batch.schema.metadata
                            ):
                                channel_fields: list[pyarrow.field] = list(
                                    batch.schema
                                )[1:]
                                for field in channel_fields:
                                    metadata[field.name] = Channel.from_field(field)
                                schemas[key] = batch.schema

                            blocks.append(
                                SeriesBlock.from_column_batch(batch, metadata)
                            )

                        # generate synchronized blocks
                        yield combine_blocks(*blocks)

    def fetch(
        self,
        channels: list[str],
        start: float,
        end: float,
    ) -> SeriesBlock:
        """Fetch timeseries data

        Parameters
        ----------
        channels : list[str]
            List of channels to request.
        start : float
            GPS start time, in seconds.
        end : float
            GPS end time, in seconds.

        Returns
        -------
        SeriesBlock
            Dictionary-like object containing all requested channel data.

        """
        return concatenate_blocks(*self.stream(channels, start, end))

    def _stream_channel_metadata(
        self,
        client: flight.FlightClient,
        descriptor: flight.FlightDescriptor,
    ) -> Generator[Channel, None, None]:
        """stream channel metadata."""
        flight_info = get_flight_info(client, descriptor)
        with MultiEndpointStream(flight_info.endpoints, client) as stream:
            for channel_meta in stream.unpack():
                yield Channel(
                    channel_meta["channel"],
                    data_type=numpy.dtype(channel_meta["data_type"]),
                    sample_rate=channel_meta["sample_rate"],
                    publisher=channel_meta["publisher"],
                    partition_id=channel_meta["partition_id"],
                    partition_index=channel_meta["partition_index"],
                )


def _parse_data_types(
    data_types: DataTypeLike | None,
) -> list[str]:
    """Parse numpy-like data types to be JSON-serializable."""
    if data_types is None:
        return []
    if isinstance(data_types, (str, type, numpy.dtype)):
        return [numpy.dtype(data_types).name]
    return [numpy.dtype(dtype).name for dtype in data_types]
