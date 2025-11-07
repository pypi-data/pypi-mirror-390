import json

import pytest
from jsonschema import ValidationError

from ... import constants
from ...flight import RequestType, RequestValidator, create_descriptor, parse_command


@pytest.fixture(scope="module")
def validator():
    return RequestValidator()


@pytest.mark.parametrize("request_type", [RequestType.Find, RequestType.Count])
@pytest.mark.parametrize("pattern", [constants.DEFAULT_MATCH, "H1:*"])
@pytest.mark.parametrize("data_type", [["float32"], ["int64", "float64"]])
@pytest.mark.parametrize("min_rate", [constants.MIN_SAMPLE_RATE, 1024])
@pytest.mark.parametrize("max_rate", [constants.MAX_SAMPLE_RATE, 1024])
@pytest.mark.parametrize("publisher", [[], ["H1-CAL"], ["H1-CAL", "H1-DAQ"]])
def test_request_find_count_valid(
    validator, request_type, pattern, data_type, min_rate, max_rate, publisher
):
    descriptor = create_descriptor(
        request_type,
        pattern=pattern,
        data_type=data_type,
        min_rate=min_rate,
        max_rate=max_rate,
        publisher=publisher,
        validator=validator,
    )
    cmd = descriptor.command
    request, args = parse_command(cmd, validator=validator)

    assert request_type is request
    assert pattern == args["pattern"]
    assert data_type == args["data_type"]
    assert min_rate == args["min_rate"]
    assert max_rate == args["max_rate"]
    assert publisher == args["publisher"]


@pytest.mark.parametrize(
    "channels", [["H1:CAL-STRAIN"], ["H1:FAKE-CHANNEL1", "H1:FAKE-CHANNEL2"]]
)
def test_request_describe_valid(validator, channels):
    descriptor = create_descriptor(
        RequestType.Describe,
        channels=channels,
        validator=validator,
    )
    cmd = descriptor.command
    request, args = parse_command(cmd, validator=validator)

    assert request is RequestType.Describe
    assert channels == args["channels"]


@pytest.mark.parametrize(
    "channels", [["H1:CAL-STRAIN"], ["H1:FAKE-CHANNEL1", "H1:FAKE-CHANNEL2"]]
)
@pytest.mark.parametrize("start", [None, 0, 1234567800])
@pytest.mark.parametrize("end", [None, 1000, 1234568000])
def test_request_stream_valid(validator, channels, start, end):
    descriptor = create_descriptor(
        RequestType.Stream,
        channels=channels,
        start=start,
        end=end,
        validator=validator,
    )
    cmd = descriptor.command
    request, args = parse_command(cmd, validator=validator)

    assert request is RequestType.Stream
    assert channels == args["channels"]


@pytest.mark.parametrize("publisher_id", ["H1-CAL", "H1-DAQ"])
def test_request_partition_valid(validator, publisher_id):
    descriptor = create_descriptor(
        RequestType.Partition,
        publisher_id=publisher_id,
        validator=validator,
    )
    cmd = descriptor.command
    request, args = parse_command(cmd, validator=validator)

    assert request is RequestType.Partition
    assert publisher_id == args["publisher_id"]


@pytest.mark.parametrize("publisher_id", ["H1-CAL", "H1-DAQ"])
def test_request_publish_valid(validator, publisher_id):
    descriptor = create_descriptor(
        RequestType.Publish,
        publisher_id=publisher_id,
        validator=validator,
    )
    cmd = descriptor.command
    request, args = parse_command(cmd, validator=validator)

    assert request is RequestType.Publish
    assert publisher_id == args["publisher_id"]


def test_create_command_invalid_schema(validator):
    with pytest.raises(ValidationError):
        create_descriptor(
            RequestType.Stream,
            publisher="DAQ",
            validator=validator,
        )


def test_parse_command_invalid_schema(validator):
    request = {
        "request": "Stream",
        "args": {
            "start": None,
            "end": None,
        },
    }
    cmd = json.dumps(request).encode("utf-8")
    with pytest.raises(ValidationError):
        parse_command(cmd, validator=validator)


def test_parse_command_invalid_json(validator):
    cmd = b"{ foo: 'bar'}"
    with pytest.raises(json.JSONDecodeError):
        parse_command(cmd, validator=validator)
