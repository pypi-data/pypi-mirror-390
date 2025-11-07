import shlex

import numpy

from ...channel import Channel


def test_count(script_runner, mock_server):
    cmd = "arrakis count H1:TEST-CHANNEL*"
    result = script_runner.run(shlex.split(cmd))
    assert result.success
    assert result.stdout.rstrip() == "2"

    cmd = "arrakis count H1:TEST-STATE*"
    result = script_runner.run(shlex.split(cmd))
    assert result.success
    assert result.stdout.rstrip() == "1"


def test_find(script_runner, mock_server, mock_channels):
    cmd = "arrakis find --json H1:TEST*"
    result = script_runner.run(shlex.split(cmd))
    assert result.success
    for line in result.stdout.splitlines():
        channel = Channel.from_json(line)
        assert channel == mock_channels[channel.name]


def test_describe(script_runner, mock_server):
    cmd = "arrakis describe --json H1:TEST-CHANNEL_COS"
    result = script_runner.run(shlex.split(cmd))
    assert result.success

    channel = Channel.from_json(result.stdout.rstrip())
    assert channel.domain == "H1"
    assert channel.data_type == numpy.float64
    assert channel.sample_rate == 16384


def test_stream(script_runner, mock_server):
    start = 1000000000
    end = 1000000010
    duration = end - start

    cmd = f"arrakis stream --start {start} --end {end} H1:TEST-STATE_ONES"
    result = script_runner.run(shlex.split(cmd))
    assert result.success
    blocks = result.stdout.splitlines()
    assert len(blocks) == duration * 16
