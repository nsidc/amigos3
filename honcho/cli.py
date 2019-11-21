import argparse
import logging

import honcho.logs as logs
from honcho.version import version
from honcho.core.system import shutdown, reboot
from honcho.config import GPIO

logger = logging.getLogger(__name__)


def init_parsers():
    common_parser = argparse.ArgumentParser(prog="honcho", add_help=False)

    common_parser.add_argument(
        "--log-level",
        help="Set logging level (DEBUG, INFO, ERROR)",
        action='store',
        default=None,
        choices=('DEBUG', 'INFO', 'ERROR'),
    )
    common_parser.add_argument('-v', '--version', action='version', version=version)

    parser = argparse.ArgumentParser(parents=[common_parser])
    subparsers = parser.add_subparsers(help='Commands', dest='command')

    return parser, subparsers


def sched_handler(args):
    import honcho.core.sched as sched

    if args.run:
        sched.execute()


def add_schedule_parser(subparsers):
    parser = subparsers.add_parser('schedule')
    parser.set_defaults(handler=sched_handler)

    parser.add_argument(
        "-r", "--run", help="Run schedule", action="store_true", dest='run'
    )


def add_power_parser(subparsers):
    import honcho.core.gpio as gpio

    parser = subparsers.add_parser('power')

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--hub-on",
        help="Hub on",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.HUB),
        dest='callbacks',
    )
    group.add_argument(
        "--hub-off",
        help="Hub off",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.HUB),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--gps-on",
        help="GPS on",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.GPS),
        dest='callbacks',
    )
    group.add_argument(
        "--gps-off",
        help="GPS off",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.GPS),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--wxt-on",
        help="Weather station on",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.WXT),
        dest='callbacks',
    )
    group.add_argument(
        "--weather-off",
        help="Weather station off",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.WXT),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--cr1000-on",
        help="cr1000 on",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.CRX),
        dest='callbacks',
    )
    group.add_argument(
        "--cr1000-off",
        help="cr1000 off",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.CRX),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--imm-on",
        help="imm on",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.IMM),
        dest='callbacks',
    )
    group.add_argument(
        "--imm-off",
        help="imm off",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.IMM),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--router-on",
        help="Router on",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.RTR),
        dest='callbacks',
    )
    group.add_argument(
        "--router-off",
        help="Router off",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.RTR),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--iridium-on",
        help="Iridium on",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.IRD),
        dest='callbacks',
    )
    group.add_argument(
        "--iridium-off",
        help="Iridium off",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.IRD),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--win-on",
        help="Windows box on",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.WIN),
        dest='callbacks',
    )
    group.add_argument(
        "--win-off",
        help="Windows box off",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.WIN),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dts-on",
        help="dts on",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.DTS),
        dest='callbacks',
    )
    group.add_argument(
        "--dts-off",
        help="dts off",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.DTS),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--sbd-on",
        help="power on serial dtx pin",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.SBD),
        dest='callbacks',
    )
    group.add_argument(
        "--sbd-off",
        help="power off iridium serial dtx pin",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.SBD),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--solar-on",
        help="power on solar sensor",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.SOL),
        dest='callbacks',
    )
    group.add_argument(
        "--solar-off",
        help="power off solar sensor",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.SOL),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--serial-on",
        help="Enable serial tx",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_on(GPIO.SER),
        dest='callbacks',
    )
    group.add_argument(
        "--serial-off",
        help="Disable serial tx",
        action="append_const",
        default=[],
        const=lambda: gpio.turn_off(GPIO.SER),
        dest='callbacks',
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--all-off",
        help="power off all gpio",
        action="append_const",
        default=[],
        const=lambda: gpio.all_off(),
        dest='callbacks',
    )
    group.add_argument(
        "--shutdown",
        help="power down all peripherals and shutdown system",
        action="append_const",
        default=[],
        const=shutdown,
        dest='callbacks',
    )
    group.add_argument(
        "--reboot",
        help="reboot system",
        action="append_const",
        default=[],
        const=reboot,
        dest='callbacks',
    )


def sbd_handler(args):
    import honcho.core.sbd as sbd

    if args.message:
        sbd.send_message(args.message)
    elif args.send_queued:
        sbd.send_queue()
    elif args.clear_queued:
        sbd.clear_queue()


def add_sbd_parser(subparsers):
    parser = subparsers.add_parser('sbd')
    parser.set_defaults(handler=sbd_handler)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--send", help="Send sbd message", action="store", dest='message', default=''
    )
    group.add_argument(
        "--send-queued",
        help="Send queued SBDs",
        action="store_true",
        dest='send_queued',
    )
    group.add_argument(
        "--clear-queued",
        help="Clear queued SBDs",
        action="store_true",
        dest='clear_queued',
    )


def orders_handler(args):
    import honcho.core.orders as orders

    if args.get:
        orders.get_orders()
    if args.perform:
        orders.perform_orders()
    if args.report:
        orders.report_results()
    if args.cleanup:
        orders.clean_up()


def add_orders_parser(subparsers):
    parser = subparsers.add_parser('orders')
    parser.set_defaults(handler=orders_handler)

    parser.add_argument("--get", help="Get orders", action="store_true", dest='get')
    parser.add_argument(
        "--perform", help="Perform orders", action="store_true", dest='perform'
    )
    parser.add_argument(
        "--report-results",
        help="Report results",
        action="store_true",
        dest='report_results',
    )
    parser.add_argument(
        "--clean-up",
        help="Clean up orders and results",
        action="store_true",
        dest='clean_up',
    )


def build_parser():
    parser, subparsers = init_parsers()
    add_schedule_parser(subparsers)
    add_power_parser(subparsers)
    add_sbd_parser(subparsers)
    add_orders_parser(subparsers)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    logs.init_logging(directory=None)

    if hasattr(args, 'callbacks'):
        for callback in args.callbacks:
            callback()

    if hasattr(args, 'handler'):
        args.handler(args)


if __name__ == "__main__":
    main()
