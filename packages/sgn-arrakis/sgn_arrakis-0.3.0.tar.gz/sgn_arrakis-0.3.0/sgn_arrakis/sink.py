import contextlib
import queue
import threading
from dataclasses import dataclass

import numpy
import numpy.ma
from arrakis import Publisher, SeriesBlock
from arrakis.block import Freq
from sgnts.base import AdapterConfig, Offset, SeriesBuffer, TSSink


def buffers_to_masked_array(
    bufs: SeriesBuffer,
    dtype: numpy.dtype,
) -> numpy.ma.MaskedArray:
    """convert list of SeriesBuffer objects into a numpy masked array

    Returns a single masked array, with the data from all buffers in
    the frame, with the data from gap bufers masked out.

    """
    return numpy.ma.concatenate(
        [
            numpy.ma.array(
                buf.filleddata(),
                mask=buf.data is None,
                dtype=dtype,
            )
            for buf in bufs
        ]
    )


@dataclass
class ArrakisSink(TSSink):
    """Sink element that streams channel data to Arrakis.

    Sink pads should be named after the channel that they will
    publish into Arrakis.

    Parameters
    ----------
    publisher_id : str
        admin-assigned publisher ID
    block_duration : int
        the duration (in nanoseconds) of data to publish in a single block.
        Default is 1/16th of a second.

    """

    publisher_id: str | None = None
    block_duration: int = 16 * Freq.Hz

    def __post_init__(self) -> None:
        if not self.publisher_id:
            msg = "must specify publisher ID"
            raise ValueError(msg)

        # setup the adapter config for the audioadapter
        # ensure data is aligned to second boundaries
        if self.adapter_config is not None:
            msg = (
                "specifying AdapterConfig is not supported in this element "
                "as they are handled internally."
            )
            raise RuntimeError(msg)
        stride = Offset.fromns(self.block_duration)
        self.adapter_config: AdapterConfig = AdapterConfig(
            stride=stride, align_to=stride
        )

        super().__post_init__()
        self.publisher = Publisher(self.publisher_id)
        self.queue: queue.Queue = queue.Queue()
        self.exception_event = threading.Event()
        # publish in a background thread so that we don't eat time
        # from the main sgn graph execution (makes internal pad
        # execution ~10x faster)
        self.thread = threading.Thread(target=self._arrakis_publish)

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.publisher.register()
        pub_chans = set(self.publisher.channels.keys())
        if set(self.sink_pad_names) != pub_chans:
            msg = f"sink pad names do not match all publisher channels {pub_chans}"
            raise ValueError(msg)
        self.thread.start()

    def stop(self):
        if self.thread and self.thread.is_alive():
            self.thread.join()

    def _arrakis_publish(self) -> None:
        # FIXME: check that we're not falling behind, maybe by
        # checking that the queue isn't growing in size
        try:
            with self.publisher as publisher:
                while True:
                    if self.at_eos:
                        break
                    with contextlib.suppress(queue.Empty):
                        sblock = self.queue.get(
                            block=True,
                            timeout=1,
                        )
                    publisher.publish(sblock)
        except Exception:
            self.exception_event.set()
            raise

    def internal(self) -> None:
        # the super method creates the self.preparedframes dictionary
        # containing all the input frames keyed by the corresponding
        # sink pad
        super().internal()

        if self.exception_event.is_set():
            self.stop()
            msg = "exception raised in resource thread, aborting."
            raise RuntimeError(msg)

        self.start()

        time_ns: int | None = None
        series: dict[str, numpy.ma.MaskedArray] = {}

        for channel_name, channel in self.publisher.channels.items():
            pad = self.snks[channel_name]
            frame = self.preparedframes[pad]

            if frame.EOS:
                self.mark_eos(pad)

            time_ns = Offset.tons(frame.offset)
            # FIXME: check continuity

            data = buffers_to_masked_array(frame, numpy.dtype(channel.data_type))

            assert frame.sample_rate == channel.sample_rate
            assert data.dtype == channel.data_type

            series[channel_name] = data.reshape(-1)

        assert time_ns

        sblock = SeriesBlock(
            time_ns,
            series,
            self.publisher.channels,
        )

        self.queue.put(sblock)
