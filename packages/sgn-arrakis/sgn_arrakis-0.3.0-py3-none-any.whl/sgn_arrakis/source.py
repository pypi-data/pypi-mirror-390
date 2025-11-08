import contextlib
import logging
from dataclasses import dataclass

import arrakis
from sgn.base import SourcePad
from sgn.subprocess import WorkerContext
from sgnts.base import Offset, SeriesBuffer, TSResourceSource

logger = logging.getLogger(__name__)


@dataclass
class ArrakisSource(TSResourceSource):
    """Source element that streams channel data from Arrakis.

    Source pads should be named after the channel they will stream
    from Arrakis.

    start_time: Optional[int] = None
        start time of stream, or "now" if None.
    duration: Optional[int] = None
        duration of stream, or endless stream if None.
    in_queue_timeout: int = 60
        How long to wait for a block from the Arrakis server before
        timing out with an error.

    """

    def __post_init__(self):
        super().__post_init__()

    @staticmethod
    def worker_process(
        context: WorkerContext,
        source_pad_names: list[str],
        srcs: dict[str, SourcePad],
        start_time: int | None,
        end_time: int | None,
    ) -> None:
        """Worker process method for streaming data from Arrakis.

        This method is called repeatedly by the TSResourceSource framework.
        Each call should process one block of data and return.
        """
        # Initialize the stream iterator on first call
        if "stream_iter" not in context.state:
            context.state["stream_iter"] = arrakis.stream(
                source_pad_names, start_time, end_time
            )

        stream_iter = context.state["stream_iter"]

        # Check if we should stop
        if context.should_stop():
            # Close the generator to clean up threads
            if stream_iter is not None and hasattr(stream_iter, "close"):
                with contextlib.suppress(Exception):
                    stream_iter.close()
            return

        try:
            # Get one block from the stream
            block = next(stream_iter)

            # Process all channels in this block
            for name, series in block.items():
                channel = series.channel

                # FIXME: should we do this for every block?
                assert (
                    channel.sample_rate in Offset.ALLOWED_RATES
                ), f"channel {name} has an invalid sample rate: {channel.sample_rate}"
                # FIXME: should we do other checks?

                if series.has_nulls:
                    # create a gap buffer
                    # FIXME: this should take the masked array and produce a
                    # set of gap and non-gap buffers. however, this isn't
                    # possible by returning buffers (instead of frames) since
                    # this would break the continuity assumption. once this is
                    # addressed upstream we should be able to handle this
                    # better
                    buf = SeriesBuffer(
                        offset=Offset.fromns(series.time_ns),
                        shape=series.data.shape,
                        sample_rate=int(series.sample_rate),
                    )
                else:
                    buf = SeriesBuffer(
                        offset=Offset.fromns(series.time_ns),
                        data=series.data,
                        sample_rate=int(series.sample_rate),
                    )
                pad = srcs[name]

                # Put data into the queue for the main thread
                context.output_queue.put((pad, buf))

                # Check if we should stop after sending each buffer
                if context.should_stop():
                    # Close the generator before returning
                    if stream_iter is not None and hasattr(stream_iter, "close"):
                        with contextlib.suppress(Exception):
                            stream_iter.close()
                    return

        except StopIteration:
            # Stream has ended - signal shutdown
            context.shutdown_event.set()
            return
        except Exception:
            # Log the original error with full context before cleanup
            logger.exception("ArrakisSource worker error")

            # On any error, ensure we close the generator
            if stream_iter is not None and hasattr(stream_iter, "close"):
                try:
                    stream_iter.close()
                except (AttributeError, RuntimeError) as close_error:
                    logger.warning("Failed to close stream iterator: %s", close_error)
            # Re-raise the exception
            raise
