import argparse
import logging

import honcho.logs  # noqa - has to be 1st
from honcho.version import version
from honcho.config import GPIO, UNIT, LOOK_PTZ
from honcho.util import ensure_all_dirs
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

    if args.run:
        sched.execute()
    if args.summary:
        sched.print_summary()


def add_schedule_parser(subparsers):
    parser = subparsers.add_parser('schedule')
    parser.set_defaults(handler=sched_handler)

    parser.add_argument("--run", help="Run schedule", action="store_true", dest='run')
    parser.add_argument(
        "--summary", help="Show schedule summary", action="store_true", dest='summary'
    )


def gpio_handler(args):
    import honcho.core.gpio as gpio

    if args.turn_on:
        for component in args.turn_on:
            gpio.turn_on(component)
    if args.turn_off:
        for component in args.turn_off:
            gpio.turn_off(component)
    if args.all_off:
        gpio.all_off()
    if args.list:
        gpio.list()


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

    group.add_argument(
        "--all-off", help="Turn off all gpio", action="store_true", dest='all_off'
    )

    group.add_argument(
        "--list", help="List gpio status", action="store_true", dest='list'
    )


def system_handler(args):
    from honcho.core.system import shutdown, reboot

    if args.shutdown:
        shutdown()
    if args.reboot:
        reboot()


def add_system_parser(subparsers):
    parser = subparsers.add_parser('system')
    parser.set_defaults(handler=system_handler)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--shutdown",
        help="power down all peripherals and shutdown system",
        action="store_true",
        dest='shutdown',
    )
    group.add_argument(
        "--reboot", help="reboot system", action="store_true", dest='reboot'
    )


def onboard_handler(args):
    import honcho.core.gpio as gpio
    import honcho.core.onboard as onboard

    if args.voltage or args.all:
        print('Voltage: {0}'.format(onboard.get_voltage()))

    if args.current or args.all:
        print('Current: {0}'.format(onboard.get_current()))

    if args.temperature or args.all:
        print('Temperature: {0}'.format(onboard.get_temperature()))

    if args.humidity or args.all:
        print('Humidity: {0}'.format(onboard.get_humidity()))

    if args.solar or args.all:
        with gpio.powered([GPIO.SOL]):
            print('Solar: {0}'.format(onboard.get_solar()))


def add_onboard_parser(subparsers):
    parser = subparsers.add_parser('onboard')
    parser.set_defaults(handler=onboard_handler)

    parser.add_argument(
        "-a", "--all", help="Check all onboard sensors", action="store_true", dest='all'
    )

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

    parser.add_argument(
        "-s", "--solar", help="Check solar", action="store_true", dest='solar'
    )


def sbd_handler(args):
    sbd = import_task('sbd')

    if args.message:
        sbd.send(args.message)
    elif args.list:
        sbd.print_queue()
    elif args.clear:
        sbd.clear_queue()
    elif args.run:
        sbd.execute()


def add_sbd_parser(subparsers):
    parser = subparsers.add_parser('sbd')
    parser.set_defaults(handler=sbd_handler)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--send", help="Send sbd message", action="store", dest='message', default=''
    )
    group.add_argument(
        "--list", help="List queued SBDs", action="store_true", dest='list'
    )
    group.add_argument(
        "--clear", help="Clear queued SBDs", action="store_true", dest='clear'
    )
    group.add_argument(
        "--run", help="Send queued SBDs", action="store_true", dest='run'
    )


def solar_handler(args):
    solar = import_task('solar')

    if args.run:
        solar.execute()


def add_solar_parser(subparsers):
    parser = subparsers.add_parser('solar')
    parser.set_defaults(handler=solar_handler)

    parser.add_argument(
        "--run", help="Execute routine", action="store_true", dest='run'
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
        orders.cleanup()
    if args.run:
        orders.execute()


def add_orders_parser(subparsers):
    parser = subparsers.add_parser('orders')
    parser.set_defaults(handler=orders_handler)

    parser.add_argument("--get", help="Get orders", action="store_true", dest='get')
    parser.add_argument(
        "--perform", help="Perform orders", action="store_true", dest='perform'
    )
    parser.add_argument(
        "--report", help="Report results", action="store_true", dest='report'
    )
    parser.add_argument(
        "--clean-up",
        help="Clean up orders and results",
        action="store_true",
        dest='cleanup',
    )
    parser.add_argument(
        "--run", help="Execute routine", action="store_true", dest='run'
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
        samples = aquadopp.get_recent_samples(device_ids, n=args.n)

        aquadopp.print_samples(samples)

    if args.run:
        aquadopp.execute()


def add_aquadopp_parser(subparsers):
    parser = subparsers.add_parser('aquadopp')
    parser.set_defaults(handler=aquadopp_handler)

    parser.set_defaults(callbacks=[])

    parser.add_argument("--get", help="Get sample(s)", action="store_true", dest='get')
    parser.add_argument("--id", help="Device id", action="store", dest='device_id')
    parser.add_argument(
        "-n", help="Number of samples", action="store", dest='n', type=int, default=1
    )

    parser.add_argument(
        "--run", help="Execute routine", action="store_true", dest='run'
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
        if args.all:
            samples = seabird.get_all_samples(device_ids)
        else:
            samples = seabird.get_recent_samples(device_ids, args.n)

        seabird.print_samples(samples)

    if args.status:
        print(seabird.print_status(device_ids))

    if args.run:
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
    parser.add_argument("--id", help="Device id", action="store", dest='device_id')
    parser.add_argument(
        "-n", help="Number of samples", action="store", dest='n', type=int, default=5
    )
    parser.add_argument(
        "--all", help="Get all samples", action="store_true", dest='all'
    )
    parser.add_argument(
        "--status", help="Get device status", action="store_true", dest='status'
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
        "--run", help="Execute routine", action="store_true", dest='run'
    )

    parser.add_argument("--stop", help="Stop logging", action="store_true", dest='stop')


def dts_handler(args):
    dts = import_task('dts')

    if args.run:
        dts.execute()


def add_dts_parser(subparsers):
    parser = subparsers.add_parser('dts')
    parser.set_defaults(handler=dts_handler)

    parser.add_argument(
        "--run", help="Execute routine", action="store_true", dest='run'
    )


def upload_handler(args):
    upload = import_task('upload')

    if args.upload_filepath:
        with upload.ftp_session() as session:
            upload.upload(args.upload_filepath, session)
    if args.list:
        upload.print_queue()
    if args.clear:
        upload.clear_queue()
    if args.run:
        upload.execute()


def add_upload_parser(subparsers):
    parser = subparsers.add_parser('upload')
    parser.set_defaults(handler=upload_handler)

    parser.add_argument(
        "--run", help="Execute routine", action="store_true", dest='run'
    )

    parser.add_argument(
        "--upload", help="Upload single file", action="store", dest='upload_filepath'
    )

    parser.add_argument(
        "--list", help="List files queued to upload", action="store_true", dest='list'
    )

    parser.add_argument(
        "--clear", help="Clear upload queue", action="store_true", dest='clear'
    )


def camera_handler(args):
    camera = import_task('camera')

    if not all(el is None for el in (args.pan, args.tilt, args.zoom)):
        pan = float(args.pan) if args.pan is not None else None
        tilt = float(args.tilt) if args.tilt is not None else None
        zoom = float(args.zoom) if args.zoom is not None else None
        camera.set_ptz(pan, tilt, zoom)
    if args.snapshot:
        camera.snapshot('snapshot.jpg')
    if args.look:
        ptz = LOOK_PTZ[args.look.upper()]
        camera.set_ptz(*ptz)
    if args.run:
        camera.execute()


def add_camera_parser(subparsers):
    parser = subparsers.add_parser('camera')
    parser.set_defaults(handler=camera_handler)

    parser.add_argument(
        "--run", help="Execute routine", action="store_true", dest='run'
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
    parser.add_argument(
        "--look", help="Look at preconfigured location", action="store", dest='look'
    )


def crx_handler(args):
    crx = import_task('crx')
    if args.run:
        crx.execute()


def add_crx_parser(subparsers):
    parser = subparsers.add_parser('crx')
    parser.set_defaults(handler=crx_handler)

    parser.add_argument(
        "--run", help="Execute routine", action="store_true", dest='run'
    )


def weather_handler(args):
    weather = import_task('weather')

    if args.get:
        samples = weather.get_samples(args.n)
        if args.average:
            samples = [weather.average_samples(samples)]

        weather.print_samples(samples)
    if args.run:
        weather.execute()


def add_weather_parser(subparsers):
    parser = subparsers.add_parser('weather')
    parser.set_defaults(handler=weather_handler)

    parser.add_argument(
        "--get", help="Get measurement", action="store_true", dest='get'
    )
    parser.add_argument(
        "--run", help="Execute routine", action="store_true", dest='run'
    )


def gps_handler(args):
    gps = import_task('gps')
    binex = import_task('binex')
    tps = import_task('tps')

    if args.get_gga:
        sample = gps.get_gga()
        gps.print_samples([sample], gps.CONVERSION_TO_STRING)
    if args.get_binex:
        binex.get_binex()
    if args.get_tps:
        tps.get_tps()

    if args.run_gga:
        gps.execute()
    if args.run_binex:
        binex.execute()
    if args.run_tps:
        tps.execute()


def add_gps_parser(subparsers):
    parser = subparsers.add_parser('gps')
    parser.set_defaults(handler=gps_handler)

    parser.add_argument(
        "--run-gga", help="Execute gga routine", action="store_true", dest='run_gga'
    )
    parser.add_argument(
        "--run-binex",
        help="Execute binex routine",
        action="store_true",
        dest='run_binex',
    )
    parser.add_argument(
        "--run-tps", help="Execute tps routine", action="store_true", dest='run_tps'
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


def supervise_handler(args):
    supervise = import_task('supervise')

    if args.run:
        supervise.execute()
    if args.history:
        supervise.print_task_history()
    if args.health:
        supervise.print_health()


def add_supervise_parser(subparsers):
    parser = subparsers.add_parser('supervise')
    parser.set_defaults(handler=supervise_handler)

    parser.add_argument(
        "--run", help="Execute supervise routine", action="store_true", dest='run'
    )
    parser.add_argument(
        "--history", help="Print task history", action="store_true", dest='history'
    )
    parser.add_argument(
        "--health", help="Print health check", action="store_true", dest='health'
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
    add_upload_parser(subparsers)
    add_imm_parser(subparsers)
    add_camera_parser(subparsers)
    add_crx_parser(subparsers)
    add_weather_parser(subparsers)
    add_solar_parser(subparsers)
    add_gps_parser(subparsers)
    add_supervise_parser(subparsers)

    return parser


def main():
    ensure_all_dirs()

    parser = build_parser()
    args = parser.parse_args()

    if hasattr(args, 'callbacks'):
        for callback in args.callbacks:
            callback()

    if hasattr(args, 'handler'):
        args.handler(args)


if __name__ == "__main__":
    main()
