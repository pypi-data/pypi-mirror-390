# Copyright (c) 2022, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/ngdd/arrakis-python/-/raw/main/LICENSE

"""Clientless API access."""

from collections.abc import Generator

from . import constants
from .block import SeriesBlock
from .channel import Channel
from .client import Client, DataTypeLike


def find(
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
        Minimum sample rate for channels.
    max_rate : int, optional
        Maximum sample rate for channels.
    publisher : str | list[str], optional
        If set, find all channels associated with these publishers.

    Yields
    -------
    Channel
        Channel objects for all channels matching query.

    """
    yield from Client().find(pattern, data_type, min_rate, max_rate, publisher)


def count(
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
        Minimum sample rate for channels.
    max_rate : int, optional
        Maximum sample rate for channels.
    publisher : str | list[str], optional
        If set, find all channels associated with these publishers.

    Returns
    -------
    int
        The number of channels matching query.

    """
    return Client().count(pattern, data_type, min_rate, max_rate, publisher)


def describe(channels: list[str]) -> dict[str, Channel]:
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
    return Client().describe(channels)


def stream(
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
    yield from Client().stream(channels, start, end)


def fetch(
    channels: list[str],
    start: float,
    end: float,
) -> SeriesBlock:
    """Fetch timeseries data

    Parameters
    ----------
    channels : list[str]
        A list of channels to request.
    start : float
        GPS start time, in seconds.
    end : float
        GPS end time, in seconds.

    Returns
    -------
    SeriesBlock
        Series block with all channels requested.

    """
    return Client().fetch(channels, start, end)
