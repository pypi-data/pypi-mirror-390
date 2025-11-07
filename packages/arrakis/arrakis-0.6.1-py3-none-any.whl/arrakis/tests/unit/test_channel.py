import numpy
import pytest

from ...channel import Channel


@pytest.fixture(scope="module")
def channel():
    return Channel(
        "H1:FKE-TEST_CHANNEL",
        data_type=numpy.dtype(numpy.float64),
        sample_rate=128,
    )


def test_invalid_channel():
    with pytest.raises(ValueError):
        Channel("INVALID", data_type=numpy.dtype(numpy.float32), sample_rate=64)


def test_valid_channel():
    domain = "H1"
    name = f"{domain}:FKE-TEST_CHANNEL"
    channel = Channel(name, data_type=numpy.dtype(numpy.float64), sample_rate=128)

    assert domain == channel.domain
    assert name == str(channel)


def test_json_round_trip(channel):
    payload = channel.to_json()
    channel_rt = Channel.from_json(payload)
    assert channel_rt == channel
