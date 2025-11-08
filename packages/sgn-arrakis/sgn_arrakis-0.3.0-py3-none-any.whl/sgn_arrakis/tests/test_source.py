from dataclasses import dataclass, field
from typing import Dict, MutableSequence
from unittest.mock import patch

import numpy as np
import pytest
from arrakis.block import Series, Time
from arrakis.channel import Channel
from sgn import Pipeline, SignalEOS
from sgnts.base import Offset, SeriesBuffer, TSSink
from sgnts.sinks import NullSeriesSink

from sgn_arrakis import ArrakisSource


@dataclass
class TSCollectSink(TSSink):
    """CollectSink for time series frames (TSFrames)."""

    collects: Dict[str, MutableSequence] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        # Initialize collections for each sink pad
        for pad_name in self.sink_pad_names:
            self.collects[pad_name] = []

    def internal(self) -> None:
        super().internal()  # Creates self.preparedframes

        for pad_name, pad in self.snks.items():
            frame = self.preparedframes[pad]
            self.collects[pad_name].append(frame)
            if frame.EOS:
                self.mark_eos(pad)


def test_arrakis_source_pipeline(mock_server):
    channels = ["H1:TEST-CHANNEL_SIN", "H1:TEST-CHANNEL_COS"]

    source = ArrakisSource(
        source_pad_names=channels,
        start_time=1000000000,
        duration=10,
    )
    sink = NullSeriesSink(
        sink_pad_names=channels,
        verbose=False,  # Reduce test output
    )

    link_map = {sink.snks[channel]: source.srcs[channel] for channel in channels}

    pipeline = Pipeline()
    pipeline.insert(
        source,
        sink,
        link_map=link_map,
    )

    with SignalEOS():
        pipeline.run()


def test_sample_rate_validation():
    """Test that invalid sample rates trigger assertion error."""
    # Create real arrakis objects with invalid sample rate
    channel = Channel(
        name="H1:TEST-CHANNEL",
        sample_rate=12345,  # Invalid rate not in Offset.ALLOWED_RATES
        data_type="float32",
    )

    series = Series(channel=channel, time_ns=1000000000, data=np.array([1.0, 2.0, 3.0]))

    mock_block = {"H1:TEST-CHANNEL": series}

    # Mock arrakis.stream to return our test data
    import sgn_arrakis.source

    def mock_stream_generator(*args, **kwargs):
        """Generator that yields the invalid sample rate block once then stops."""
        yield mock_block
        return  # Explicitly stop the generator

    with patch.object(
        sgn_arrakis.source.arrakis, "stream", return_value=mock_stream_generator()
    ):
        source = ArrakisSource(
            source_pad_names=["H1:TEST-CHANNEL"],
            start_time=1,
            duration=1,
            in_queue_timeout=1,
        )

        # Create a simple sink to trigger the pipeline
        sink = TSCollectSink(sink_pad_names=["H1:TEST-CHANNEL"])

        # Create link map and pipeline
        link_map = {sink.snks["H1:TEST-CHANNEL"]: source.srcs["H1:TEST-CHANNEL"]}
        pipeline = Pipeline()
        pipeline.insert(source, sink, link_map=link_map)

        # Running the pipeline should trigger the assertion error in the worker
        with (
            SignalEOS(),
            pytest.raises(RuntimeError, match="worker stopped before EOS") as exc_info,
        ):
            pipeline.run()

        # Walk through the exception chain to find the original AssertionError
        exc: BaseException | None = exc_info.value
        original_assertion_found = False
        while exc is not None:
            if isinstance(exc, AssertionError) and "invalid sample rate: 12345" in str(
                exc
            ):
                original_assertion_found = True
                break
            exc = exc.__cause__

        assert (
            original_assertion_found
        ), f"Original AssertionError not found in exception chain: {exc_info.value}"


def test_gap_and_data_handling():
    """Test ArrakisSource gap vs data handling."""
    channel_name = "H1:TEST-CHANNEL"
    channel = Channel(
        name=channel_name,
        sample_rate=16384,  # Valid rate
        data_type="float32",
    )

    # Block 1: Normal data - 1 second worth of data
    start_time_ns = 1000000000
    normal_data = np.random.randn(int(channel.sample_rate)).astype(
        np.float32
    )  # 16384 samples = 1 second
    normal_series = Series(channel=channel, time_ns=start_time_ns, data=normal_data)

    # Block 2: Gap data - 1 second worth of gaps
    next_time_ns = start_time_ns + normal_series.duration_ns
    gap_data = np.ma.array(
        np.zeros(int(channel.sample_rate)),
        mask=np.ones(int(channel.sample_rate), dtype=bool),
        dtype=np.float32,
    )
    gap_series = Series(channel=channel, time_ns=next_time_ns, data=gap_data)

    mock_blocks = [{channel_name: normal_series}, {channel_name: gap_series}]

    # Mock arrakis.stream to return our test data
    import sgn_arrakis.source

    def mock_stream_generator(*args, **kwargs):
        """Generator that yields blocks sequentially."""
        for block in mock_blocks:
            yield block

    with patch.object(
        sgn_arrakis.source.arrakis, "stream", return_value=mock_stream_generator()
    ):
        # Create source with calculated time range (start_time in seconds)
        source = ArrakisSource(
            source_pad_names=[channel_name],
            start_time=start_time_ns // Time.s,
            duration=2.0,
            in_queue_timeout=5,
        )

        # Create sink
        sink = TSCollectSink(sink_pad_names=[channel_name])

        # Create link map and pipeline
        link_map = {sink.snks[channel_name]: source.srcs[channel_name]}
        pipeline = Pipeline()
        pipeline.insert(source, sink, link_map=link_map)

        # Run pipeline
        with SignalEOS():
            pipeline.run()

    # Verify that both frames were collected
    assert len(sink.collects) == 1, "Should have one channel collection"
    pad_key = next(iter(sink.collects.keys()))
    collected_frames = sink.collects[pad_key]
    assert len(collected_frames) == 2, "Should have collected 2 frames"

    # First frame should contain normal data buffer
    frame1 = collected_frames[0]
    buffer1 = frame1[0]
    assert isinstance(buffer1, SeriesBuffer)
    assert np.array_equal(
        buffer1.data, normal_data
    ), "First frame should have normal data"
    assert buffer1.offset == Offset.fromns(start_time_ns)

    # Second frame should contain gap buffer
    frame2 = collected_frames[1]
    buffer2 = frame2[0]
    assert isinstance(buffer2, SeriesBuffer)
    assert buffer2.data is None, "Second frame should be a gap buffer (no data)"
    assert buffer2.shape == (
        16384,
    ), "Gap buffer should have correct shape for 1 second of data at 16384 Hz"
    assert buffer2.offset == Offset.fromns(next_time_ns)
