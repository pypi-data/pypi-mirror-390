# Copyright (c) 2022, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/ngdd/arrakis-python/-/raw/main/LICENSE

"""Arrow Flight utilities."""

from __future__ import annotations

import concurrent.futures
import contextlib
import json
import logging
import os
import queue
import threading
from enum import IntEnum, auto
from importlib import resources
from typing import TYPE_CHECKING, Any, TypedDict
from unittest.mock import sentinel
from urllib.parse import urlparse

import arrakis_schema
import jsonschema
from pyarrow import flight
from pyarrow.flight import connect

from . import constants

if TYPE_CHECKING:
    from collections.abc import Generator
    from datetime import timedelta


logger = logging.getLogger("arrakis")


EOS = sentinel.EOS


class RequestType(IntEnum):
    Stream = auto()
    Describe = auto()
    Find = auto()
    Count = auto()
    Publish = auto()
    Partition = auto()


class Request(TypedDict):
    request: str
    args: dict[str, Any]


class RequestValidator:
    """A validator for JSON-encoded requests."""

    def __init__(self) -> None:
        self._validators: dict[RequestType, jsonschema.Draft7Validator] = {}

        # load generic descriptor schema
        resource = resources.files(arrakis_schema).joinpath("descriptor.json")
        with resources.as_file(resource) as path:
            schema = json.loads(path.read_text())
        self._generic_validator = jsonschema.Draft7Validator(schema)

    def validate(self, payload: Request) -> None:
        """Validate a JSON-encoded request.

        Parameters
        ----------
        payload : Request
            A dictionary with a 'request' and an 'args' key encoding
            the given Flight request.

        Raises
        ------
        ValidationError
            If the request does not match the expected schema.

        """
        self._generic_validator.validate(payload)
        request = RequestType[payload["request"]]

        # load schema on demand
        if request not in self._validators:
            resource = resources.files(arrakis_schema).joinpath(
                f"{request.name.lower()}.json"
            )
            with resources.as_file(resource) as path:
                schema = json.loads(path.read_text())
            self._validators[request] = jsonschema.Draft7Validator(schema)

        self._validators[request].validate(payload)


def parse_url(url: str | None) -> str:
    if url is None:
        url = os.getenv("ARRAKIS_SERVER", constants.DEFAULT_ARRAKIS_SERVER)
    assert url is not None, "ARRAKIS_SERVER not specified."
    parsed = urlparse(url, scheme="grpc")
    if parsed.scheme != "grpc":
        msg = f"invalid URL {url}. if scheme is specified, it must start with grpc://"
        raise ValueError(msg)
    return parsed.geturl()


def create_command(
    request_type: RequestType, *, validator: RequestValidator, **kwargs
) -> bytes:
    """Create a Flight command containing a JSON-encoded request.

    Parameters
    ----------
    request_type : RequestType
        The type of request.
    validator : RequestValidator
        A validator to validate that the command matches the expected schema.
    **kwargs : dict, optional
        Extra arguments corresponding to the specific request.

    Returns
    -------
    bytes
        The JSON-encoded request.

    Raises
    ------
    ValidationError
        If the request does not match the expected schema.

    """
    cmd: Request = {
        "request": request_type.name,
        "args": kwargs,
    }
    validator.validate(cmd)
    return json.dumps(cmd).encode("utf-8")


def create_descriptor(
    request_type: RequestType, *, validator: RequestValidator, **kwargs
) -> flight.FlightDescriptor:
    """Create a Flight descriptor given a request.

    Parameters
    ----------
    request_type : RequestType
        The type of request.
    validator : RequestValidator
        A validator to validate that the command matches the expected schema.
    **kwargs : dict, optional
        Extra arguments corresponding to the specific request.

    Returns
    -------
    flight.FlightDescriptor
        A Flight Descriptor containing the request.

    Raises
    ------
    ValidationError
        If the request does not match the expected schema.

    """
    cmd = create_command(request_type, validator=validator, **kwargs)
    return flight.FlightDescriptor.for_command(cmd)


def parse_command(
    cmd: bytes, *, validator: RequestValidator
) -> tuple[RequestType, dict]:
    """Parse a Flight command into a request.

    Parameters
    ----------
    cmd : bytes
        The JSON-encoded request.
    validator : RequestValidator
        A validator to validate that the command matches the expected schema.

    Returns
    -------
    request_type : RequestType
        The type of request.
    kwargs : dict
        Arguments corresponding to the specific request.

    Raises
    ------
    JSONDecodeError
        If the command does not decode to valid JSON.
    ValidationError
        If the request does not match the expected schema.

    """
    try:
        parsed = json.loads(cmd.decode("utf-8"))
    except json.JSONDecodeError as e:
        msg = "Command does not decode to valid JSON"
        raise json.JSONDecodeError(msg, e.doc, e.pos) from e
    else:
        validator.validate(parsed)
        return RequestType[parsed["request"]], parsed["args"]


class MultiEndpointStream(contextlib.AbstractContextManager):
    """Multi-threaded Arrow Flight endpoint stream iterator context manager

    Given a list of endpoints, connect to all of them in parallel and
    stream data from them all interleaved.

    """

    def __init__(
        self,
        endpoints: list[flight.FlightEndpoint],
        initial_client: flight.FlightClient,
    ):
        """initialize with list of endpoints and an reusable flight client"""
        self.endpoints = endpoints
        self.initial_client = initial_client
        self.q: queue.SimpleQueue = queue.SimpleQueue()
        self.quit_event: threading.Event = threading.Event()
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.endpoints),
        )
        self.threads_done = {endpoint.serialize(): False for endpoint in endpoints}
        self.futures: list[concurrent.futures.Future] | None = None

    def _execute_endpoint(self, endpoint: flight.FlightEndpoint):
        logger.debug("endpoint: %s", endpoint)
        # FIXME: endpoints can contain multiple locations from which
        # the ticket can be served, considered as data replicas.  we
        # should cycle through backup locations if there are
        # connection issues with the primary one.
        location = endpoint.locations[0]
        # if an endpoint is specified with the special location:
        #   "arrow-flight-reuse-connection://?"
        # then the initial client connection will be reused.
        # see: https://arrow.apache.org/docs/format/Flight.html#connection-reuse
        scheme = urlparse(location.uri.decode()).scheme
        if scheme == "arrow-flight-reuse-connection":
            context: contextlib.AbstractContextManager[flight.FlightClient]
            context = contextlib.nullcontext(self.initial_client)
        else:
            context = connect(location)
        with context as client:
            try:
                for chunk in client.do_get(endpoint.ticket):
                    if self.quit_event.is_set():
                        break
                    self.q.put((chunk, endpoint))
            finally:
                self.q.put((EOS, endpoint))

    def __iter__(
        self,
        timeout: timedelta = constants.DEFAULT_QUEUE_TIMEOUT,
    ) -> Generator[
        flight.FlightStreamReader
        | tuple[flight.FlightStreamReader, flight.FlightEndpoint],
        None,
        None,
    ]:
        """Execute the streams and yield the results

        Yielded results are a tuple of the data chunk, and the
        endpoint it came from.

        The timeout is expected to be a timedelta object.

        """
        self.futures = [
            self.executor.submit(self._execute_endpoint, endpoint)
            for endpoint in self.endpoints
        ]

        while not all(self.threads_done.values()):
            try:
                data, endpoint = self.q.get(block=True, timeout=timeout.total_seconds())
            except queue.Empty:
                pass
            else:
                if data is EOS:
                    self.threads_done[endpoint.serialize()] = True
                else:
                    yield data, endpoint
            for future in self.futures:
                if future.done() and future.exception():
                    self.quit_event.set()

    stream = __iter__

    def unpack(self):
        """Unpack stream data into individual elements"""
        for chunk, _ in self:
            yield from chunk.data.to_pylist()

    def close(self):
        """close all streams"""
        self.quit_event.set()
        if self.futures is not None:
            for f in self.futures:
                # re-raise exceptions to the client, returning
                # user-friendly Flight-specific errors when relevant
                try:
                    f.result()
                except flight.FlightError as e:
                    # NOTE: this strips the original message of everything
                    # besides the original error message raised by the server
                    msg = e.args[0].partition(" Detail:")[0]
                    raise type(e)(msg, e.extra_info) from None

        self.executor.shutdown(cancel_futures=True)
        self.futures = None

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
