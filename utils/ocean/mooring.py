import argparse
import logging
import os

from serial import Serial

import aquadopp
import imm
import seabird

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DATA_DIR = "seabird_data"
CHUNK_DIR = os.path.join([DATA_DIR, "chunks"])


def init_parsers():
    common_parser = argparse.ArgumentParser(prog="honcho", add_help=False)

    common_parser.add_argument(
        "--log-level",
        help="Set logging level (DEBUG, INFO, ERROR)",
        action="store",
        default=None,
        choices=("DEBUG", "INFO", "ERROR"),
    )
    common_parser.add_argument(
        "--port",
        help="Set port for serial connection to IMM",
        action="store",
        default=imm.DEFAULT_PORT,
    )
    common_parser.add_argument(
        "--baud",
        help="Set baud rate for serial connection to IMM",
        action="store",
        default=imm.DEFAULT_BAUD,
    )

    parser = argparse.ArgumentParser(parents=[common_parser])
    subparsers = parser.add_subparsers(help="Commands", dest="command")

    return parser, subparsers


def imm_handler(args):
    if args.status:
        with imm.active_line(args.port, args.baud) as serial:
            print(imm.get_status_xml(serial))
            print(imm.discovery(serial))
    elif args.console:
        imm.console(port=args.port, baud=args.baud)


def add_imm_parser(subparsers):
    parser = subparsers.add_parser("imm")
    parser.set_defaults(handler=imm_handler)
    parser.add_argument("--status", help="Query imm status", action="store_true")
    parser.add_argument(
        "--console", help="Get interactive console session", action="store_true"
    )


def seabird_handler(args):
    if args.status:
        with imm.active_line(args.port, args.baud) as serial:
            print(seabird.get_status_xml(serial, args.device_id))
    else:
        seabird.pull_samples(
            device_id=args.device_id,
            start=args.start,
            end=args.end,
            chunk_size=args.chunk_size,
            port=args.port,
            baud=args.baud,
        )


def add_seabird_parser(subparsers):
    parser = subparsers.add_parser("seabird")
    parser.set_defaults(handler=seabird_handler)

    parser.add_argument(
        "--start",
        help="Set starting sample to pull (default = first)",
        action="store",
        default=None,
    )
    parser.add_argument(
        "--end",
        help="Set end sample to pull (default = last)",
        action="store",
        default=None,
    )
    parser.add_argument(
        "--device-id",
        help="Set device-id for seabird to access",
        action="store",
        default=None,
    )
    parser.add_argument("--status", help="Query device status", action="store_true")


def aquadopp_handler(args):
    if args.status:
        with imm.active_line(args.port, args.baud) as serial:
            print(aquadopp.get_status_xml(serial, args.device_id))
    else:
        aquadopp.pull_samples(
            device_id=args.device_id,
            start=args.start,
            end=args.end,
            chunk_size=args.chunk_size,
            port=args.port,
            baud=args.baud,
        )


def add_aquadopp_parser(subparsers):
    parser = subparsers.add_parser("aquadopp")
    parser.set_defaults(handler=aquadopp_handler)

    parser.add_argument(
        "--start",
        help="Set starting sample to pull (default = first)",
        action="store",
        default=None,
    )
    parser.add_argument(
        "--end",
        help="Set end sample to pull (default = last)",
        action="store",
        default=None,
    )
    parser.add_argument(
        "--device-id",
        help="Set device-id for aquadopp to access",
        action="store",
        default=None,
    )
    parser.add_argument("--status", help="Query device status", action="store_true")


if __name__ == "__main__":
    parser, subparsers = init_parsers()
    add_imm_parser(subparsers)
    add_seabird_parser(subparsers)
    add_aquadopp_parser(subparsers)
    args = parser.parse_args()

    if hasattr(args, "callbacks"):
        for callback in args.callbacks:
            callback()

    if hasattr(args, "handler"):
        args.handler(args)
