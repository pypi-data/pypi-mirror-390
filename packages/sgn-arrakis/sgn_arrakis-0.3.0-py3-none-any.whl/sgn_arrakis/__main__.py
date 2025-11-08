import argparse
import logging
import os

from arrakis import Client
from sgn import Pipeline, SignalEOS
from sgnts.sinks import NullSeriesSink
from sgnts.sources import FakeSeriesSource

from . import ArrakisSink, ArrakisSource, __version__


def main() -> None:
    for logname in ["sgn-ts", "arrakis"]:
        logger = logging.getLogger(logname)
        logger.setLevel(os.getenv("LOG_LEVEL", "DEBUG").upper())
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(message)s"))
        logger.addHandler(handler)

    parser = argparse.ArgumentParser(
        description="Arrakis Source/Sink test application",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
    )
    parser.add_argument(
        "--url",
        "-u",
        type=str,
        help="initial server url",
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        metavar="",
        dest="cmd",
    )

    sp = subparsers.add_parser(
        "source",
        help="channel streaming (ArrakisSource to NullSeriesSink)",
    )
    sp.add_argument(
        "channels",
        metavar="channel",
        nargs="+",
        help="channels to stream",
    )

    sp = subparsers.add_parser(
        "sink",
        help="channel publication (FakeSeriesSource to ArrakisSink)",
        description="This will stream zeros to all publisher channels.",
    )
    sp.add_argument(
        "publisher_id",
        help="publisher ID",
    )
    sp.add_argument(
        "--include-gaps",
        dest="ngap",
        action="store_const",
        const=-1,
        default=0,
        help="include gaps in the source stream",
    )

    args = parser.parse_args()

    if args.cmd == "source":
        channels = args.channels

        source = ArrakisSource(
            source_pad_names=channels,
        )
        sink = NullSeriesSink(
            sink_pad_names=channels,
            verbose=True,
        )

    elif args.cmd == "sink":
        channels = {
            channel.name: channel
            for channel in Client(args.url).find(publisher=args.publisher_id)
        }

        signals = {}
        for name, channel in channels.items():
            signals[name] = {
                "signal-type": "const",
                "sample-shape": (1,),
                "sample-rate": channel.sample_rate,
                "value": channel.data_type.type(1),
            }

        source = FakeSeriesSource(
            source_pad_names=channels,
            signals=signals,
            ngap=args.ngap,
            real_time=True,
        )
        sink = ArrakisSink(
            publisher_id=args.publisher_id,
            sink_pad_names=channels,
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


if __name__ == "__main__":
    main()
