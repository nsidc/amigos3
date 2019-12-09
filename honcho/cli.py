import argparse
import logging

import honcho.logs as logs
from honcho.version import version
from honcho.core.system import shutdown, reboot
from honcho.config import GPIO, UNIT
from honcho.tasks import import_task

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

    if args.execute:
        sched.execute()


def add_schedule_parser(subparsers):
    parser = subparsers.add_parser('schedule')
    parser.set_defaults(handler=sched_handler)

    parser.add_argument(
        "--execute", help="Run schedule", action="store_true", dest='execute'
    )


def gpio_handler(args):
    import honcho.core.gpio as gpio

    if args.turn_on:
        for component in args.turn_on:
            gpio.turn_on(component)
    if args.turn_off:
        for component in args.turn_off:
            gpio.turn_off(component)


def add_gpio_parser(subparsers):
    parser = subparsers.add_parser('gpio')
    parser.set_defaults(handler=gpio_handler)

    for component in GPIO:
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--{0}-on".format(component.lower()),
            help="Turn on {0}".format(component),
            action="append_const",
            default=[],
            const=component,
            dest='turn_on',
        )
        group.add_argument(
            "--{0}-off".format(component.lower()),
            help="Turn off {0}".format(component),
            action="append_const",
            default=[],
            const=component,
            dest='turn_off',
        )


def add_system_parser(subparsers):
    parser = subparsers.add_parser('system')

    group = parser.add_mutually_exclusive_group()
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


def onboard_handler(args):
    import honcho.core.onboard as onboard

    if args.voltage:
        print('Voltage: {0}'.format(onboard.get_voltage()))

    if args.current:
        print('Current: {0}'.format(onboard.get_current()))

    if args.temperature:
        print('Temperature: {0}'.format(onboard.get_temperature()))

    if args.humidity:
        print('Humidity: {0}'.format(onboard.get_humidity()))


def add_onboard_parser(subparsers):
    parser = subparsers.add_parser('onboard')
    parser.set_defaults(handler=onboard_handler)

    parser.add_argument(
        "-v",
        "--voltage",
        help="Check supply voltage",
        action="store_true",
        dest='voltage',
    )

    parser.add_argument(
        "-c",
        "--current",
        help="Check supply current",
        action="store_true",
        dest='current',
    )

    parser.add_argument(
        "-t",
        "--temperature",
        help="Check temperature",
        action="store_true",
        dest='temperature',
    )

    parser.add_argument(
        "-H", "--humidity", help="Check humidity", action="store_true", dest='humidity'
    )


def sbd_handler(args):
    sbd = import_task('sbd')

    if args.message:
        sbd.send(args.message)
    elif args.send_queued:
        sbd.execute()
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
    orders = import_task('orders')

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


def imm_handler(args):
    import honcho.core.imm as imm

    if args.repl:
        imm.repl()


def add_imm_parser(subparsers):
    parser = subparsers.add_parser('imm')
    parser.set_defaults(handler=imm_handler)

    parser.add_argument(
        "--repl", help="Start imm repl", action="store_true", dest='repl'
    )


def aquadopp_handler(args):
    aquadopp = import_task('aquadopp')

    if args.device_id:
        device_ids = [args.device_id]
    else:
        device_ids = UNIT.AQUADOPP_IDS

    if args.get:
        samples = aquadopp.get_recent_samples(device_ids, args.n)

        aquadopp.print_samples(samples)

    if args.execute:
        aquadopp.execute()


def add_aquadopp_parser(subparsers):
    parser = subparsers.add_parser('aquadopp')
    parser.set_defaults(handler=aquadopp_handler)

    parser.set_defaults(callbacks=[])

    parser.add_argument("--get", help="Get sample(s)", action="store_true", dest='get')
    parser.add_argument("--id", help="Device id", action="store", dest='device_id')
    parser.add_argument(
        "-n", help="Number of samples", action="store", dest='n', type=int, default=5
    )

    parser.add_argument(
        "--execute", help="Execute routine", action="store_true", dest='execute'
    )


def seabird_handler(args):
    seabird = import_task('seabird')

    if args.device_id:
        device_ids = [args.device_id]
    else:
        device_ids = UNIT.SEABIRD_IDS

    if args.set:
        if args.interval:
            seabird.set_interval(device_ids, args.interval)

    if args.start:
        seabird.start(device_ids)

    if args.get:
        if args.average:
            samples = seabird.get_averaged_samples(device_ids, args.n)
        else:
            samples = seabird.get_recent_samples(device_ids, args.n)

        seabird.print_samples(samples)

    if args.execute:
        seabird.execute()

    if args.stop:
        seabird.stop(device_ids)


def add_seabird_parser(subparsers):
    parser = subparsers.add_parser('seabird')
    parser.set_defaults(handler=seabird_handler)
    parser.set_defaults(callbacks=[])

    parser.add_argument(
        "--start", help="Start logging", action="store_true", dest='start'
    )

    parser.add_argument("--get", help="Get sample(s)", action="store_true", dest='get')
    parser.add_argument(
        "--average", help="Get averaged sample(s)", action="store_true", dest='average'
    )
    parser.add_argument("--id", help="Device id", action="store", dest='device_id')
    parser.add_argument(
        "-n", help="Number of samples", action="store", dest='n', type=int, default=5
    )

    parser.add_argument("--set", help="Set parameters", action="store_true", dest='set')
    parser.add_argument(
        "--interval",
        help="Set sampling interval",
        action="store",
        dest='interval',
        type=int,
    )

    parser.add_argument(
        "--execute", help="Execute routine", action="store_true", dest='execute'
    )

    parser.add_argument("--stop", help="Stop logging", action="store_true", dest='stop')


def dts_handler(args):
    dts = import_task('dts')

    if args.execute:
        dts.execute()


def add_dts_parser(subparsers):
    parser = subparsers.add_parser('dts')
    parser.set_defaults(handler=dts_handler)

    parser.add_argument(
        "--execute", help="Execute routine", action="store_true", dest='execute'
    )


def data_handler(args):
    archive = import_task('archive')

    if args.upload_filepath:
        archive.upload([args.upload_filepath])
    if args.archive:
        archive.archive()
    if args.archive_data:
        archive.archive_data()
    if args.archive:
        archive.archive_logs()
    if args.execute:
        archive.execute()


def add_data_parser(subparsers):
    parser = subparsers.add_parser('data')
    parser.set_defaults(handler=dts_handler)

    parser.add_argument(
        "--execute", help="Execute routine", action="store_true", dest='execute'
    )

    parser.add_argument(
        "--upload", help="Upload single file", action="store", dest='upload_filepath'
    )

    parser.add_argument(
        "--archive",
        help="Rotate data and logs into archive",
        action="store_true",
        dest='archive',
    )

    parser.add_argument(
        "--archive-data",
        help="Rotate data into archive",
        action="store_true",
        dest='archive_data',
    )

    parser.add_argument(
        "--archive-logs",
        help="Rotate logs into archive",
        action="store_true",
        dest='archive_logs',
    )


def camera_handler(args):
    camera = import_task('camera')

    if not all(el is None for el in (args.pan, args.tilt, args.zoom)):
        camera.set_ptz(float(args.pan), float(args.tilt), float(args.zoom))
    if args.snapshot:
        camera.snapshot('snapshot.jpg')


def add_camera_parser(subparsers):
    parser = subparsers.add_parser('camera')
    parser.set_defaults(handler=camera_handler)

    parser.add_argument(
        "--execute", help="Execute routine", action="store_true", dest='execute'
    )

    parser.add_argument(
        "--pan", help="Pan to value (-1 to 1)", action="store", dest='pan'
    )
    parser.add_argument(
        "--tilt", help="Tilt to value (-1 to 1)", action="store", dest='tilt'
    )
    parser.add_argument(
        "--zoom", help="Zoom to value (0 to 1)", action="store", dest='zoom'
    )

    parser.add_argument(
        "--snapshot", help="Take snapshot", action="store_true", dest='snapshot'
    )


def cr1000x_handler():
    pass


def add_cr1000x_parser(subparsers):
    parser = subparsers.add_parser('cr1000x')
    parser.set_defaults(handler=cr1000x_handler)

    parser.add_argument(
        "--execute", help="Execute routine", action="store_true", dest='execute'
    )


def weather_handler(args):
    weather = import_task('weather')

    if args.get:
        samples = weather.get_samples(args.n)
        if args.average:
            samples = [weather.average_samples(samples)]

        weather.print_samples(samples)
    if args.execute:
        weather.execute()


def add_weather_parser(subparsers):
    parser = subparsers.add_parser('weather')
    parser.set_defaults(handler=weather_handler)

    parser.add_argument(
        "--get", help="Get measurement", action="store_true", dest='get'
    )
    parser.add_argument(
        "--execute", help="Execute routine", action="store_true", dest='execute'
    )


def gps_handler(args):
    gps = import_task('gps')
    binex = import_task('binex')
    tps = import_task('tps')

    if args.get_gga:
        sample = gps.get_gga()
        gps.print_samples([sample])
    if args.get_binex:
        binex.get_binex()
    if args.get_tps:
        tps.get_tps()

    if args.execute_gga:
        gps.execute()
    if args.execute_binex:
        binex.execute()
    if args.execute_tps:
        tps.execute()


def add_gps_parser(subparsers):
    parser = subparsers.add_parser('gps')
    parser.set_defaults(handler=gps_handler)

    parser.add_argument(
        "--execute-gga",
        help="Execute gga routine",
        action="store_true",
        dest='execute_gga',
    )
    parser.add_argument(
        "--execute-binex",
        help="Execute binex routine",
        action="store_true",
        dest='execute_binex',
    )
    parser.add_argument(
        "--execute-tps",
        help="Execute tps routine",
        action="store_true",
        dest='execute_tps',
    )

    parser.add_argument(
        "--get-gga", help="Get GGA data", action="store_true", dest='get_gga'
    )
    parser.add_argument(
        "--get-binex", help="Get binex data", action="store_true", dest='get_binex'
    )
    parser.add_argument(
        "--get-tps", help="Get binex data", action="store_true", dest='get_tps'
    )


def build_parser():
    parser, subparsers = init_parsers()
    add_schedule_parser(subparsers)
    add_gpio_parser(subparsers)
    add_system_parser(subparsers)
    add_sbd_parser(subparsers)
    add_orders_parser(subparsers)
    add_onboard_parser(subparsers)
    add_aquadopp_parser(subparsers)
    add_seabird_parser(subparsers)
    add_dts_parser(subparsers)
    add_data_parser(subparsers)
    add_imm_parser(subparsers)
    add_camera_parser(subparsers)
    add_cr1000x_parser(subparsers)
    add_weather_parser(subparsers)
    add_gps_parser(subparsers)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    logs.init_logging()

    if hasattr(args, 'callbacks'):
        for callback in args.callbacks:
            callback()

    if hasattr(args, 'handler'):
        args.handler(args)


if __name__ == "__main__":
    main()
