import os
from pathlib import Path

import pytest

arrakis_server = pytest.importorskip("arrakis_server")

from arrakis_server.backends.mock import MockBackend
from arrakis_server.metadata import ChannelConfigBackend
from arrakis_server.server import ArrakisFlightServer


@pytest.fixture(scope="session")
def mock_backend():
    channel_file = Path(__file__).parent / "data" / "channels.toml"
    return MockBackend(channel_files=[channel_file])


@pytest.fixture(scope="session")
def mock_server(mock_backend):
    with ArrakisFlightServer(url=None, backend=mock_backend) as server:
        os.environ["ARRAKIS_SERVER"] = server.url
        yield server


@pytest.fixture(scope="module")
def mock_channels():
    channel_file = Path(__file__).parent / "data" / "channels.toml"
    backend = ChannelConfigBackend()
    backend.load(channel_file)
    return backend.metadata
