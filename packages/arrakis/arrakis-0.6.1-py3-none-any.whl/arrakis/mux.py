# Copyright (c) 2022, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/ngdd/arrakis-server/-/raw/main/LICENSE

import heapq
import logging
import warnings
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum, auto
from typing import Generic, TypeVar

import gpstime
import numpy

from .block import Time

logger = logging.getLogger("arrakis")

T = TypeVar("T")

DEFAULT_TIMEOUT = timedelta(seconds=1)


class OnDrop(Enum):
    IGNORE = auto()
    RAISE = auto()
    WARN = auto()


@dataclass
class MuxedData(Mapping, Generic[T]):
    """Container that holds timestamped data.

    Parameters
    ----------
    time : int
        The timestamp associated with this data, in nanoseconds.
    data : dict[str, T]
        The keyed data.

    """

    time: int
    data: dict[str, T]

    def __getitem__(self, index: str) -> T:
        return self.data[index]

    def __iter__(self) -> Iterator[str]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)


class Muxer(Generic[T]):
    """A data structure that multiplexes items from multiple named streams.

    Given items from multiple named streams with monotonically increasing
    integer timestamps, this data structure can be used to pull out sets of
    synchronized items (items all with the same timestamp).

    The oldest items will be held until either all named streams are
    available or until the timeout has been reached. If a start time has been
    set, any items with an older timestamp will be rejected.

    Parameters
    ----------
    keys : Iterable[str]
        Identifiers for the named streams to expect when adding items.
    start : int, optional
        The GPS time to start muxing items for.
        If not set, accept items from any time.
    timeout : timedelta or None, optional
        The maximum time to wait for messages from named streams, in seconds,
        before multiplexing. If None is specified, wait indefinitely. Default
        is 1 second.

    """

    def __init__(
        self,
        keys: Iterable[str],
        start: int | None = None,
        timeout: timedelta | None = DEFAULT_TIMEOUT,
    ) -> None:
        self._keys = set(keys)
        self._items: dict[int, dict[str, T]] = defaultdict(lambda: defaultdict())
        self._times: list[int] = []
        self._last_time = (
            (start - 1) if start is not None else numpy.iinfo(numpy.int64).min
        )
        self._start = start
        self._timeout = timeout

        # track when processing started to handle lookback properly
        self._processing_start_time = int(gpstime.gpsnow() * Time.SECONDS)

    def push(self, time: int, key: str, item: T, on_drop: str = "warn") -> None:
        """Push an item into the muxer.

        Parameters
        ----------
        time : int
            The timestamp associated with this item.
        key : str
            The key stream associated with this item. Must match a key provided
            at initialization.
        item : T
            The item to add.
        on_drop : str, optional
            Specifies behavior when the item would be dropped from the muxer,
            in the case that it was not provided to the muxer before the
            specified timeout. Options are 'ignore', 'raise', or 'warn'.
            Default is 'warn'.

        """
        if key not in self._keys:
            msg = f"{key} doesn't match keys provided at initialization"
            raise KeyError(msg)

        # skip over items that have already been pulled
        if time <= self._last_time:
            if self._start is not None and time < self._start:
                return
            msg = f"item's timestamp is too old: ({time} <= {self._last_time})"
            match OnDrop[on_drop.upper()]:
                case OnDrop.IGNORE:
                    return
                case OnDrop.RAISE:
                    raise ValueError(msg)
                case OnDrop.WARN:
                    logger.warning(msg)
                    warnings.warn(msg, stacklevel=2)
                    return

        # add item
        if time in self._items:
            if key not in self._items[time]:
                self._items[time][key] = item
        else:
            heapq.heappush(self._times, time)
            self._items[time][key] = item

    def pull(self) -> Iterator[MuxedData[T]]:
        """Pull monotonically increasing synchronized items from the muxer.

        Yields
        ------
        MuxedData[T]
            Synchronized items with a common timestamp, keyed by stream keys.

        """
        if not self._times:
            return

        # yield items in monotonically increasing order as long
        # as conditions are met
        time = self._times[0]
        while (
            self._has_all_items(time)
            or self._are_items_stale(time)
            or self._has_complete_newer_timestamp(time)
        ):
            yield MuxedData(time, self._items.pop(time))
            self._last_time = heapq.heappop(self._times)
            if not self._times:
                break
            time = self._times[0]

    def _has_all_items(self, time: int):
        """Check if a timestamp has all items requested."""
        return len(self._items[time]) == len(self._keys)

    def _has_complete_newer_timestamp(self, time: int):
        """Check if there's a newer complete timestamp, making this one safe to yield.

        Based on monotonic timestamp assumption: if we have complete data for a newer
        timestamp, no more data will arrive for older timestamps, so we can safely
        yield partial older data.
        """
        for newer_time in self._times:
            if newer_time > time and self._has_all_items(newer_time):
                return True
        return False

    def _are_items_stale(self, time):
        """Check if a timestamp is older than the latency cutoff."""
        if self._timeout is None:
            return False

        time_now = gpstime.gpsnow()
        dt_timeout = self._timeout.total_seconds()

        if time < self._processing_start_time:
            # historical data: give extra time based on how far back in history
            dt_lookback = (self._processing_start_time - time) / float(Time.SECONDS)
            oldest_time_allowed = time_now - dt_timeout + dt_lookback
        else:
            # live data: use normal timeout
            oldest_time_allowed = time_now - dt_timeout

        return time <= int(oldest_time_allowed * Time.SECONDS)
