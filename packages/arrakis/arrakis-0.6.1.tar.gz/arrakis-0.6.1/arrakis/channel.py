# Copyright (c) 2022, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/ngdd/arrakis-python/-/raw/main/LICENSE

"""Channel information."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from functools import cached_property
from typing import TYPE_CHECKING

import numpy

if TYPE_CHECKING:
    import pyarrow


CHANNEL_NAME_RE = re.compile(
    r"^(?P<domain>.*):(?P<subsystem>[^_-]*)(?P<delimiter>[_-])(?P<rest>.*)$"
)


@dataclass(frozen=True)
class ParsedChannelName:
    """A parsed channel name

    Channel names have the following structure:

        <domain>:<subsystem>[-_]<rest>

    """

    domain: str
    subsystem: str
    subsystem_delimiter: str
    rest: str

    @classmethod
    def parse(cls, name: str) -> ParsedChannelName:
        """Parse a channel name into it's constituent parts"""
        if rem := CHANNEL_NAME_RE.match(name):
            return cls(
                rem["domain"],
                rem["subsystem"],
                rem["delimiter"],
                rem["rest"],
            )
        msg = "Invalid channel name structure."
        raise ValueError(msg)


@dataclass(frozen=True)
class Channel:
    """Metadata associated with a channel.

    Channels have the form {domain}:*.

    Parameters
    ----------
    name : str
        The name associated with this channel.
    data_type : numpy.dtype
        The data type associated with this channel.
    sample_rate : float
        The sampling rate associated with this channel.
    time : int, optional
        The timestamp when this metadata became active.
    publisher : str
        The publisher associated with this channel.
    partition_id : str, optional
        The partition ID associated with this channel.
    partition_index: int, optional
        Partition index for the channel.  It is unique within the partition and
        allows the use of an integer value to identify the channel instead of a
        string.
    expected_latency: int, optional
        Expected publication latency for this channel's data, in
        seconds.

    """

    name: str
    data_type: numpy.dtype | str
    sample_rate: float
    time: int | None = None
    publisher: str | None = None
    partition_id: str | None = None
    partition_index: int | None = None
    expected_latency: int | None = None

    def __post_init__(self) -> None:
        # cast to numpy dtype object, as raw types like numpy.float64 are not
        object.__setattr__(self, "data_type", numpy.dtype(self.data_type))
        # evaluate the parsed name to validate, will throw ValueError
        # if invalid
        _ = self.parsed_name

    @cached_property
    def parsed_name(self) -> ParsedChannelName:
        return ParsedChannelName.parse(self.name)

    @property
    def domain(self) -> str:
        return self.parsed_name.domain

    @property
    def subsystem(self) -> str:
        return self.parsed_name.subsystem

    @property
    def dtype(self):
        return self.data_type

    def __repr__(self) -> str:
        return f"<{self.name}, {self.sample_rate} Hz, {self.data_type}>"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        # name, data type and sample rate are always required to match
        is_equal = (
            self.name == other.name
            and self.dtype == other.dtype
            and self.sample_rate == other.sample_rate
        )

        # optional fields match only if both are defined
        if self.time is not None and other.time is not None:
            is_equal &= self.time == other.time
        if self.publisher and other.publisher:
            is_equal &= self.publisher == other.publisher
        if self.partition_id and other.partition_id:
            is_equal &= self.partition_id == other.partition_id

        return is_equal

    def to_json(self, time: int | None = None) -> str:
        """Serialize channel metadata to JSON.

        Parameters
        ----------
        time : int, optional
            If specified, the timestamp when this metadata became active.

        """
        # generate dict from dataclass and adjust fields
        # to be JSON compatible. In addition, store the
        # channel name, as well as updating the timestamp
        # if passed in.
        obj = asdict(self)
        obj["data_type"] = numpy.dtype(self.data_type).name
        if time is not None:
            obj["time"] = time
        obj = {k: v for k, v in obj.items() if v is not None}
        return json.dumps(obj)

    @classmethod
    def from_json(cls, payload: str) -> Channel:
        """Create a Channel from its JSON representation.

        Parameters
        ----------
        payload : str
            The JSON-serialized channel.

        Returns
        -------
        Channel
            The newly created channel.

        """
        obj = json.loads(payload)
        obj["data_type"] = numpy.dtype(obj["data_type"])
        return cls(**obj)

    @classmethod
    def from_field(cls, field: pyarrow.field) -> Channel:
        """Create a Channel from Arrow Flight field metadata.

        Parameters
        ----------
        field : pyarrow.field
            The channel field containing relevant metadata.

        Returns
        -------
        Channel
            The newly created channel.

        """
        data_type = numpy.dtype(_list_dtype_to_str(field.type))
        sample_rate = float(field.metadata[b"rate"].decode())
        return cls(field.name, data_type, sample_rate)


@dataclass(frozen=True)
class PartitionInfo:
    """Partition metadata associated with a channel.

    Parameters
    ----------
    name : str
        The name associated with this channel.
    id : str, optional
        The partition ID associated with this channel.
    index : int, optional
        Partition index for the channel.  It is unique within the partition and
        allows the use of an integer value to identify the channel instead of a
        string.

    """

    name: str
    id: str
    index: int

    @classmethod
    def from_channel(cls, channel: Channel) -> PartitionInfo:
        """Extract partition information from a Channel.

        Parameters
        ----------
        channel : Channel
            The channel containing relevant metadata.

        Returns
        -------
        PartitionInfo
            The newly created partition information.

        """
        assert channel.partition_id is not None
        assert channel.partition_index is not None
        return cls(
            name=channel.name,
            id=channel.partition_id,
            index=channel.partition_index,
        )


def _list_dtype_to_str(dtype: pyarrow.ListType) -> str:
    """Return a string representation of the list's inner data type.

    Note that this does not always match the string representation
    of Arrow's internal data types, to match the behavior across
    different languages.

    Parameters
    ----------
    dtype : pyarrow.ListType
        The list data type to inspect.

    Returns
    -------
    str
        A string representation of the list's inner data type.

    """
    inner_dtype = str(dtype.value_type)
    if inner_dtype == "float":
        return "float32"
    if inner_dtype == "double":
        return "float64"
    return inner_dtype
