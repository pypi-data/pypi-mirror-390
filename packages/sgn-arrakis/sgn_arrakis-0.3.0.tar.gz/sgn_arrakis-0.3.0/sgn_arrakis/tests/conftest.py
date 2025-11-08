import os
import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

# Skip entire module if arrakis-server not available
pytest.importorskip("arrakis_server")

from arrakis_server.backends.mock import MockBackend
from arrakis_server.metadata import ChannelConfigBackend
from arrakis_server.server import ArrakisFlightServer


@pytest.fixture(scope="session")
def test_channels_config():
    """Create a temporary channels.toml file for testing."""
    channels_toml = dedent("""
    ["H1:TEST-CHANNEL_SIN"]
    rate = 16384
    dtype = "float32"
    func = "sin(t)"

    ["H1:TEST-CHANNEL_COS"]
    rate = 16384
    dtype = "float64"
    func = "cos(t)"

    ["H1:TEST-STATE_ONES"]
    rate = 16
    dtype = "int32"
    func = "1"

    ["L1:TEST-NOISE"]
    rate = 4096
    dtype = "float32"
    func = "random()"
    """)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(channels_toml)
        f.flush()
        yield Path(f.name)

    # Cleanup
    os.unlink(f.name)


@pytest.fixture(scope="session")
def mock_backend(test_channels_config):
    """Create a mock backend with test channels."""
    return MockBackend(channel_files=[test_channels_config])


@pytest.fixture(scope="session")
def mock_server(mock_backend):
    """Create a mock Arrakis server for testing."""
    with ArrakisFlightServer(url=None, backend=mock_backend) as server:
        # Set environment variable so arrakis client can find the server
        os.environ["ARRAKIS_SERVER"] = server.url
        yield server


@pytest.fixture(scope="module")
def mock_channels(test_channels_config):
    """Load channel metadata for testing."""
    backend = ChannelConfigBackend()
    backend.load(test_channels_config)
    return backend.metadata
