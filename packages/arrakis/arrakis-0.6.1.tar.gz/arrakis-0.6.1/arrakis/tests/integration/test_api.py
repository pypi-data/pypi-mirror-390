import numpy
import pytest

import arrakis

from ...block import Time

pytestmark = pytest.mark.integration


def test_count(mock_server):
    assert arrakis.count("H1:TEST-CHANNEL*") == 2
    assert arrakis.count("H1:TEST-STATE*") == 1


def test_find(mock_server):
    channels = list(arrakis.find("H1:TEST*"))
    assert len(channels) == 3


def test_describe(mock_server):
    channels = list(arrakis.describe(["H1:TEST-CHANNEL_COS"]).values())
    assert len(channels) == 1
    channel = channels[0]

    assert channel.domain == "H1"
    assert channel.data_type == numpy.float64
    assert channel.sample_rate == 16384


def test_fetch(mock_server):
    channel = "H1:TEST-STATE_ONES"
    start = 1000000000
    end = 1000000010
    duration = end - start
    sample_rate = 16
    data_type = numpy.int32

    block = arrakis.fetch([channel], start, end)
    series = block[channel]

    assert block.time_ns == start * Time.SECONDS
    assert block.duration_ns == duration * Time.SECONDS
    assert len(block.channels) == 1

    assert series.time_ns == start * Time.SECONDS
    assert series.duration_ns == duration * Time.SECONDS
    assert series.name == channel
    assert series.data_type == data_type
    assert series.sample_rate == sample_rate

    expected = numpy.ones(duration * sample_rate, dtype=numpy.int32)
    assert numpy.allclose(series.data, expected)
