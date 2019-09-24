# -*- coding: utf-8 -*-
import logging
from time import sleep

import honcho.argparse as argparse
import honcho.logs as logs
from honcho.version import version

logger = logging.getLogger(__name__)


def init_parsers():
    common_parser = argparse.ArgumentParser(
        prog="honcho", version=version, add_help=False
    )
    common_parser.add_argument(
        "--log-level",
        help="Set logging level (DEBUG, INFO, ERROR)",
        action='store',
        default='INFO',
        choices=('DEBUG', 'INFO', 'ERROR'),
    )
    parser = argparse.ArgumentParser(parents=[common_parser])
    subparsers = parser.add_subparsers(help='Commands', dest='command')

    return parser, subparsers


def add_schedule_parser(subparsers):
    schedule = subparsers.add_parser('schedule')
    group = schedule.add_mutually_exclusive_group()
    group.add_argument(
        "-p", "--pending", help="View pending schedule", action="store_true"
    )
    group.add_argument(
        "-s", "--summer", help="View summer schedule", action="store_true"
    )
    group.add_argument(
        "-w", "--winter", help="View winter schedule", action="store_true"
    )


def add_weather_parser(subparsers):
    subparsers.add_parser('weather')


def add_cr1000x_parser(subparsers):
    subparsers.add_parser('cr1000x')


def add_solar_parser(subparsers):
    subparsers.add_parser('solar')


def add_power_parser(subparsers):
    import honcho.core.gpio as gpio

    power = subparsers.add_parser('power')

    group = power.add_mutually_exclusive_group()
    group.add_argument(
        "--hub-on",
        help="Hub on",
        action="append_const",
        default=[],
        const=gpio.hub_on,
        dest='callbacks',
    )
    group.add_argument(
        "--hub-off",
        help="Hub off",
        action="append_const",
        default=[],
        const=gpio.hub_off,
        dest='callbacks',
    )

    group = power.add_mutually_exclusive_group()
    group.add_argument(
        "--gps-on",
        help="GPS on",
        action="append_const",
        default=[],
        const=gpio.gps_on,
        dest='callbacks',
    )
    group.add_argument(
        "--gps-off",
        help="GPS off",
        action="append_const",
        default=[],
        const=gpio.gps_off,
        dest='callbacks',
    )

    group = power.add_mutually_exclusive_group()
    group.add_argument(
        "--weather-on",
        help="Weather station on",
        action="append_const",
        default=[],
        const=gpio.weather_on,
        dest='callbacks',
    )
    group.add_argument(
        "--weather-off",
        help="Weather station off",
        action="append_const",
        default=[],
        const=gpio.weather_off,
        dest='callbacks',
    )

    group = power.add_mutually_exclusive_group()
    group.add_argument(
        "--cr1000-on",
        help="cr1000 on",
        action="append_const",
        default=[],
        const=gpio.cr1000_on,
        dest='callbacks',
    )
    group.add_argument(
        "--cr1000-off",
        help="cr1000 off",
        action="append_const",
        default=[],
        const=gpio.cr1000_off,
        dest='callbacks',
    )

    group = power.add_mutually_exclusive_group()
    group.add_argument(
        "--imm-on",
        "--imm_on",
        help="imm on",
        action="append_const",
        default=[],
        const=gpio.imm_on,
        dest='callbacks',
    )
    group.add_argument(
        "--imm-off",
        "--imm_off",
        help="imm off",
        action="append_const",
        default=[],
        const=gpio.imm_off,
        dest='callbacks',
    )

    group = power.add_mutually_exclusive_group()
    group.add_argument(
        "--router-on",
        help="Router on",
        action="append_const",
        default=[],
        const=gpio.router_on,
        dest='callbacks',
    )
    group.add_argument(
        "--router-off",
        help="Router off",
        action="append_const",
        default=[],
        const=gpio.router_off,
        dest='callbacks',
    )

    group = power.add_mutually_exclusive_group()
    group.add_argument(
        "--iridium-on",
        help="Iridium on",
        action="append_const",
        default=[],
        const=gpio.iridium_on,
        dest='callbacks',
    )
    group.add_argument(
        "--iridium-off",
        help="Iridium off",
        action="append_const",
        default=[],
        const=gpio.iridium_off,
        dest='callbacks',
    )

    group = power.add_mutually_exclusive_group()
    group.add_argument(
        "--dts-on",
        help="dts on",
        action="append_const",
        default=[],
        const=gpio.dts_on,
        dest='callbacks',
    )
    group.add_argument(
        "--dts-off",
        help="dts off",
        action="append_const",
        default=[],
        const=gpio.dts_off,
        dest='callbacks',
    )

    group = power.add_mutually_exclusive_group()
    group.add_argument(
        "--sbd-on",
        help="power on serial dtx pin",
        action="append_const",
        default=[],
        const=gpio.sbd_on,
        dest='callbacks',
    )
    group.add_argument(
        "--sbd-off",
        help="power off iridium serial dtx pin",
        action="append_const",
        default=[],
        const=gpio.sbd_off,
        dest='callbacks',
    )

    group = power.add_mutually_exclusive_group()
    group.add_argument(
        "--solar-on",
        help="power on solar sensor",
        action="append_const",
        default=[],
        const=gpio.solar_on,
        dest='callbacks',
    )
    group.add_argument(
        "--solar-off",
        help="power off solar sensor",
        action="append_const",
        default=[],
        const=gpio.solar_off,
        dest='callbacks',
    )

    group = power.add_mutually_exclusive_group()
    group.add_argument(
        "--all-off",
        help="power off all gpio",
        action="append_const",
        default=[],
        const=gpio.all_off,
        dest='callbacks',
    )
    group.add_argument(
        "--shutdown",
        help="power down all peripherals and shutdown system",
        action="append_const",
        default=[],
        const=gpio.shutdown,
        dest='callbacks',
    )
    group.add_argument(
        "--reboot",
        help="reboot system",
        action="append_const",
        default=[],
        const=gpio.reboot,
        dest='callbacks',
    )


def add_serial_parser(subparsers):
    import honcho.core.gpio as gpio

    serial = subparsers.add_parser('serial')

    group = serial.add_mutually_exclusive_group()
    group.add_argument(
        "-e",
        "--enable",
        help="enable serial com",
        action="append_const",
        default=[],
        const=gpio.enable_serial,
        dest='callbacks',
    )
    group.add_argument(
        "-d",
        "--disable",
        help="disable serial com",
        action="append_const",
        default=[],
        const=gpio.disable_serial,
        dest='callbacks',
    )


def add_sbd_parser(subparsers):
    sbd = subparsers.add_parser('sbd')

    group = sbd.add_mutually_exclusive_group()
    group.add_argument("--send", help="send sbd", action="store_true")
    group.add_argument("--read", help="read sbd", action="store_true")


def add_dial_parser(subparsers):
    dial = subparsers.add_parser('dial')

    group = dial.add_mutually_exclusive_group()
    group.add_argument("--out", help="dial out files through", action="store_true")
    dial.add_argument("--in", help="Configure for dial in", action="store_true")


def add_gps_parser(subparsers):
    gps = subparsers.add_parser('gps')

    group = gps.add_mutually_exclusive_group()
    group.add_argument("--set-time", help="?", action="store_true")
    group.add_argument("--get_time", help="?", action="store_true")


def add_dts_parser(subparsers):
    pass


def add_sleep_parser(subparsers):
    sleep = subparsers.add_parser('sleep')

    group = sleep.add_mutually_exclusive_group()

    group.add_argument("--on", help="Turn on sleepy mode", action="store_true")
    group.add_argument("--off", help="Turn off sleepy mode", action="store_true")


def add_camera_parser(subparsers):
    camera = subparsers.add_parser('camera')

    group = camera.add_mutually_exclusive_group()
    camera.add_argument(
        "-t", "--tilt", help="Set tilt", action="store", type=float, default=None
    )
    camera.add_argument(
        "-p", "--pan", help="Set pan", action="store", type=float, default=None
    )
    camera.add_argument(
        "-z", "--zoom", help="Set zoom", action="store", type=float, default=None
    )

    group = camera.add_mutually_exclusive_group()
    group.add_argument("--snapshot", help="Take a snapshot", action="store_true")
    group.add_argument("--status", help="Get status", action="store_true")


def camera(args):
    from honcho.core.camera import ptz_client

    ptz = ptz_client()
    if set(args.pan, args.tilt, args.zoom) != {None}:
        ptz.send(typeof="absolute", pan=args.pan, tilt=args.tilt, zoom=args.zoom)
    if args.snapshot:
        ptz.snapShot()
    elif args.get_status:
        ptz.getStatus(output=True)


def cr1000x(args):
    from python.cr1000x import cr1000x_live

    CR = cr1000x_live()
    CR.cr_all()


def solar(args):
    from python.solar import solar_live

    sol = solar_live()
    sol.solar_all()


def gps(args):
    from python.gps import gps_data
    from python.gpio import gps_off, gps_on, enable_serial, disable_serial

    gps = gps_data()
    gps_on()
    enable_serial()
    sleep(30)
    if args.set_time:
        gps.update_time()
    elif args.get_time:
        print(gps.get_gpstime())
    gps_off()
    disable_serial()


def sleep_mode(args):
    if args.on:
        logger.info("Sleep mode is restored")
        with open("/media/mmcblk0p1/logs/sleep_toggle", "w+") as f:
            f.write("on")
        print("Thanks, sleep mode is restored. See you soon ")
    elif args.off:
        logger.info("Sleep mode deactivated")
        with open("/media/mmcblk0p1/logs/sleep_toggle", "w+") as f:
            f.write("off")
        print("Sleep mode is disactivated. Please remember to reactivate it")


# def dial(args):
#     raise NotImplementedError


def weather(args):
    from python.vaisala import Live_Data

    Live_Readings = Live_Data()
    Live_Readings.weather_all()


def build_parser():
    parser, subparsers = init_parsers()
    add_power_parser(subparsers)
    add_camera_parser(subparsers)
    add_sleep_parser(subparsers)
    add_cr1000x_parser(subparsers)
    add_serial_parser(subparsers)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    logs.init_logging(getattr(logging, args.log_level))

    if args.callbacks:
        for callback in args.callbacks:
            callback()

    if args.command == 'camera':
        camera(args)
    if args.command == 'cr1000':
        cr1000x(args)
    if args.command == 'gps':
        gps(args)


if __name__ == "__main__":
    main()
