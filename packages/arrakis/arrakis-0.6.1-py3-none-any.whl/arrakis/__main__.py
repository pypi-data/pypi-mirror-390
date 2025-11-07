import argparse
import logging
import os
import sys

import numpy
from gpstime import GPSTimeParseAction, gpsnow

from . import Channel, Client, __version__, constants
from .flight import flight

logger = logging.getLogger("arrakis")


##########


parser = argparse.ArgumentParser()
parser.add_argument("--version", "-v", action="version", version=__version__)
parser.add_argument(
    "--url",
    "-u",
    type=str,
    help="initial server url",
)
subparsers = parser.add_subparsers()


def add_subparser(cmd, **kwargs):
    sp = subparsers.add_parser(
        cmd.__name__,
        help=cmd.__doc__.splitlines()[0],
        description=cmd.__doc__,
        **kwargs,
    )
    sp.set_defaults(func=cmd)
    return sp


##########


def parse_pattern(pattern):
    if not pattern or pattern == "*":
        pattern = constants.DEFAULT_MATCH
    return pattern


def print_channel(chan: Channel, *, as_json: bool = False) -> None:
    output = chan.to_json() if as_json else repr(chan)
    print(output)


def _add_find_count_args(parser):
    parser.add_argument(
        "pattern",
        type=str,
        nargs="?",
        default=constants.DEFAULT_MATCH,
        help="channel pattern",
    )
    parser.add_argument(
        "--data-type",
        "--dtype",
        metavar="DTYPE",
        type=numpy.dtype,
        # action="append",
        help="data type",
    )
    parser.add_argument(
        "--min_rate",
        metavar="INT",
        type=int,
        help="minimum sample rate",
    )
    parser.add_argument(
        "--max_rate",
        metavar="INT",
        type=int,
        help="maximum sample rate",
    )
    parser.add_argument(
        "--publisher",
        metavar="ID",
        type=str,
        # action="append",
        help="publisher ID",
    )


##################################################


def find(args):
    """find channels matching regexp pattern"""
    as_json = args.json
    del args.json
    client = Client(url=args.url)
    del args.url
    for chan in client.find(**vars(args)):
        print_channel(chan, as_json=as_json)


sparser = add_subparser(find, aliases=["search", "list"])
_add_find_count_args(sparser)
sparser.add_argument(
    "-j",
    "--json",
    action="store_true",
    help="print channel output as JSON",
)


##########


def count(args):
    """count channels matching pattern"""
    client = Client(url=args.url)
    del args.url
    print(client.count(**vars(args)))


sparser = add_subparser(count)
_add_find_count_args(sparser)


##########


def describe(args):
    """describe channels"""
    as_json = args.json
    del args.json
    client = Client(url=args.url)
    del args.url
    for channel in client.describe(**vars(args)).values():
        print_channel(channel, as_json=as_json)


sparser = add_subparser(describe, aliases=["show"])
sparser.add_argument("channels", nargs="+", help="list of channels to describe")
sparser.add_argument(
    "-j",
    "--json",
    action="store_true",
    help="print channel output as JSON",
)


##########


def stream(args):
    """stream data for channels"""
    channels = args.channels
    start = None
    end = None
    if args.start:
        start = args.start.gps()
    if args.end:
        end = args.end.gps()
    client = Client(url=args.url)
    for buf in client.stream(channels, start=start, end=end):
        print(buf)
        if args.latency:
            latency = gpsnow() - buf.time
            print(f"latency: {latency} s", file=sys.stderr)


sparser = add_subparser(stream)
sparser.add_argument("channels", nargs="+", help="list of channels to stream")
sparser.add_argument(
    "--start",
    action=GPSTimeParseAction,
    help="start time (GPS or arbitrary date/time string)",
)
sparser.add_argument(
    "--end",
    action=GPSTimeParseAction,
    help="end time (GPS or arbitrary date/time string)",
)
sparser.add_argument(
    "--latency",
    action="store_true",
    help="print buffer latency to stderr",
)


##########


def fetch(args):
    """fetch data for channels"""
    args.start = args.start.gps()
    args.end = args.end.gps()
    client = Client(url=args.url)
    del args.url
    data = client.fetch(**vars(args))
    print(data)


sparser = add_subparser(fetch)
sparser.add_argument("channels", nargs="+", help="list of channels to fetch")
sparser.add_argument(
    "--start",
    required=True,
    action=GPSTimeParseAction,
    help="start time (GPS or arbitrary date/time string)",
)
sparser.add_argument(
    "--end",
    required=True,
    action=GPSTimeParseAction,
    help="end time (GPS or arbitrary date/time string)",
)


##########


def publish(args):
    """publish values to channels

    Arguments should be channel name + generator function pairs.  The
    generator function is used to generate data for the specified
    channel and should be a sympy expression, with the 't' value used
    to indicate time, e.g. "sin(t)".  A numeric value for the
    generator function will generate a constant stream.

    """
    import sched
    import time
    from math import log2

    from sympy import lambdify, parse_expr
    from sympy.abc import t

    from . import Publisher, SeriesBlock, Time

    if not args.list:
        if len(args.channel_args) % 2 != 0:
            parser.error("arguments must be channel name + generator function pairs")
        chan_funcs = {}
        for name, value in zip(args.channel_args[::2], args.channel_args[1::2]):
            expr = parse_expr(value)
            chan_funcs[name] = lambdify(t, expr, "numpy")

        if args.rate < 1 or log2(args.rate) % 1 != 0:
            parser.error("rate must be power of two.")

    publisher = Publisher(args.publisher_id, args.url)
    publisher.register()

    if args.list:
        for _name, channel in publisher.channels.items():
            print_channel(channel)
        return

    def _gen_data(publisher, tick):
        metadata = {}
        series = {}
        for name, func in chan_funcs.items():
            try:
                channel = publisher.channels[name]
            except KeyError:
                msg = f"unknown channel for publisher: {name}"
                raise ValueError(msg) from None
            time_array = numpy.arange(int(channel.sample_rate / args.rate)) + tick
            data = numpy.array(
                numpy.broadcast_to(func(time_array), time_array.shape),
                dtype=channel.data_type,
            )
            series[name] = data
            metadata[name] = channel
        sblock = SeriesBlock(
            tick * Time.SECONDS,
            series,
            metadata,
        )
        logger.info("publish: %s", sblock)
        publisher.publish(sblock)

    s = sched.scheduler(time.time, time.sleep)
    tick = int(time.time())
    with publisher:
        while True:
            tick += 1 / args.rate
            s.enterabs(tick, 0, _gen_data, (publisher, tick))
            s.run()


sparser = add_subparser(publish)
sparser.add_argument(
    "--publisher-id",
    type=str,
    required=True,
    help="publisher ID (required)",
)
sparser.add_argument(
    "--rate",
    type=int,
    default=16,
    help="publication rate, in Hz.  Must be a power of two.",
)
lgroup = sparser.add_mutually_exclusive_group()
lgroup.add_argument(
    "--list",
    action="store_true",
    help="list publisher channels and exit",
)
lgroup.add_argument(
    "channel_args",
    nargs="*",
    metavar="CHANNEL FUNC",
    default=[],
    help="channel name + generator function pairs",
)


##################################################


def main():
    logger.setLevel(os.getenv("LOG_LEVEL", "DEBUG").upper())
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(handler)

    args = parser.parse_args()

    if "func" not in args:
        parser.print_help()
        return

    func = args.func
    del args.func
    logger.debug(args)

    try:
        func(args)
    except flight.FlightError as e:
        msg = f"request error: {e}"
        raise SystemExit(msg) from e


if __name__ == "__main__":
    import signal

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
