# -*- coding: utf-8 -*-
import os.path
import amigos.argparse as argparse
import amigos.watchdog as watchdog
import amigos.gpio as gpio
from amigos.onvif.onvif import ptz_client as client
import sys
from amigos.vaisala import Average_Reading as Average_Reading
from amigos.vaisala import Live_Data as Live_Data
from amigos.device_checker import is_on,is_off
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "text.txt")
ptz = client()

# Create instances of vaisala script classes
Avg_Reading = Average_Reading()
Live_Readings = Live_Data()


def args_parser():
    val = None
    if len(sys.argv) > 3:
        val = sys.argv[-1]
        sys.argv.pop(-1)
    parser = argparse.ArgumentParser(prog='Amigos', add_help=False)
    # Group or command for schedule viewing
    schedule = parser.add_argument_group(
        'Set or View Schedules', 'Show all the schedules')
    schedule.add_argument(
        'schedule', help='View all pending schedule', nargs='?')
    schedule.add_argument(
        '-s', '--summer', help='View summer schedule', action='store_true')
    schedule.add_argument(
        '-w', '--winter', help='View winter schedule', action='store_true')

    # group of command for weather viewing
    weather = parser.add_argument_group('Read weather', 'show live weather data')
    weather.add_argument('weather', help='View all live data', nargs='?')
    weather.add_argument('-c', '--collect',
                         help='Run data averaging program', action='store_true')
    weather.add_argument('-dir', '--wind_direction',
                         help='View average wind direction (Degrees)', action='store_true')
    weather.add_argument('-speed', '--wind_speed',
                         help='View average wind speed (m/s)', action='store_true')
    weather.add_argument('-temp', '--air_temp',
                         help='View current air temperature (C)', action='store_true')
    weather.add_argument('-hum', '--humidity',
                         help='View current relative humidity (%%RH)', action='store_true')
    weather.add_argument('-pres', '--pressure',
                         help='View current air pressure (hPa)', action='store_true')
    weather.add_argument('-r_acc', '--rain_accumulation',
                         help='View rain accumulation over last storm (mm)', action='store_true')
    weather.add_argument('-r_dur', '--rain_duration',
                         help='View rain duration over last storm (s)', action='store_true')
    weather.add_argument('-r_int', '--rain_intensity',
                         help='View rain intensity over last storm (mm/hour)', action='store_true')
    weather.add_argument('-r_pint', '--rain_peak_intensity',
                         help='View rain peak intensity over last storm (mm/hour)', action='store_true')
    weather.add_argument('-h_acc', '--hail_accumulation',
                         help='View hail accumulation over last storm (hits/cm^2)', action='store_true')
    weather.add_argument('-h_dur', '--hail_duration',
                         help='View hail duration over last storm (s)', action='store_true')
    weather.add_argument('-h_int', '--hail_intensity',
                         help='View hail intensity over last storm (hits/cm^2/hour)', action='store_true')
    weather.add_argument('-h_pint', '--hail_peak_intensity',
                         help='View hail peak intensity over last storm (hits/cm^2/hour)', action='store_true')
    weather.add_argument('-unit', '--vaisala_unit',
                         help='View Vaisala unit information', action='store_true')

    #Group of commands for device checker 
    device = parser.add_argument_group('See devices ON', 'see devives OFF')
    device.add_argument('device', help='View all devices ON/OFF', nargs='?')
    device.add_argument('-run', '--running', 
                         help='Show all ON devices', action='store_true')
    device.add_argument('-n_run', '--not_running',
                        help='Show all OFF devices', action='store_true')



    # group of command for watchdog configureting
    wdog = parser.add_argument_group('Set Watchdog', 'Change watch dog setup')
    wdog.add_argument(
        'watchdog', help='View running watchdog setting', nargs='?')
    wdog.add_argument('-u', '--update',
                      help='update the watchdog cycle', action='store_true')
    wdog.add_argument('-sl', '--sleep',
                      help='Put board to sleep', action='store_true')
    wdog.add_argument('-d', '--deactivate',
                      help='deactivate watchdog from auto update', action='store_true')

    # power commands
    power = parser.add_argument_group(
        'Power Control', 'Control power on gpio pins')
    power.add_argument(
        'power', help='Need one of the secondary arguments bellow', nargs='?')
    power.add_argument('-m_on', '--modem_on',
                       help='Modem on', action='store_true')
    power.add_argument('-m_off', '--modem_off',
                       help='Modem off', action='store_true')
    power.add_argument('-g_on', '--gps_on',
                       help='GPS on', action='store_true')
    power.add_argument('-g_off', '--gps_off',
                       help='GPS off', action='store_true')
    power.add_argument('-w_on', '--weather_on',
                       help='Weather station on', action='store_true')
    power.add_argument('-w_off', '--weather_off',
                       help='Weather station off', action='store_true')
    power.add_argument('-cr_on', '--cr1000_on',
                       help='cr1000 on', action='store_true')
    power.add_argument('-cr_off', '--cr1000_off',
                       help='cr1000 off', action='store_true')
    power.add_argument('-r_on', '--router_on',
                       help='Router on', action='store_true')
    power.add_argument('-r_off', '--router_off',
                       help='Router off', action='store_true')
    power.add_argument('-i_on', '--iridium_on',
                       help='Iridium on', action='store_true')
    power.add_argument('-i_off', '--iridium_off',
                       help='Iridium off', action='store_true')
    power.add_argument('-d_on', '--dts_on',
                       help='dts on', action='store_true')
    power.add_argument('-d_off', '--dts_off',
                       help='dts off', action='store_true')
    power.add_argument('-off', '--power_off',
                       help='power down all peripherals', action='store_true')
    power.add_argument('-on', '--power_on',
                       help='power up all peripherals', action='store_true')
    power.add_argument('-r', '--reboot',
                       help='reboot system', action='store_true')

    camera = parser.add_argument_group(
        'Camera Control', 'Control camera position, take pictures and more')
    camera.add_argument(
        'camera', help='required a secondary command', nargs='?')
    camera.add_argument('-t', '--tilt',
                        help='Move camera up', action='store_true')
    camera.add_argument('-p', '--pan',
                        help='Move camera to the left', action='store_true')
    camera.add_argument('-z', '--zoom',
                        help='zoom camera to the left', action='store_true')

    camera.add_argument('-combo', '--combine_move',
                        help='execute combine move on the camera', action='store_true')
    camera.add_argument('-snap', '--snapshot',
                        help='Take a snapshot', action='store_true')
    camera.add_argument('-status', '--get_status',
                        help='get status', action='store_true')
    # help command
    h = parser.add_argument_group('Help', 'show help menu')
    h.add_argument('-h', '--help',
                   help='Show this menu', action='store_true')

    # retrieve all arguments entered
    return parser, val


def power(args):
    if args.weather_on:
        gpio.weather_on(1)
    elif args.weather_off:
        gpio.weather_off(1)
    elif args.cr1000_on:
        gpio.cr1000_on(1)
    elif args.cr1000_off:
        gpio.cr1000_off(1)
    elif args.router_on:
        gpio.router_on(1)
    elif args.router_off:
        gpio.router_off(1)
    elif args.iridium_on:
        gpio.iridium_on(1)
    elif args.iridium_off:
        gpio.iridium_off(1)
    elif args.dts_on:
        gpio.dts_on(1)
    elif args.dts_off:
        gpio.dts_off(1)
    elif args.power_off:
        gpio.power_down(1)
    elif args.power_on:
        gpio.power_up(1)
    elif args.modem_off:
        gpio.modem_off(1)
    elif args.modem_on:
        gpio.modem_on(1)
    elif args.gps_on:
        gpio.gps_on(1)
    elif args.gps_off:
        gpio.gps_off(1)
    elif args.reboot:
        gpio.reboot(1)
    else:
        print("Too few arguments. No device specified.")


def camera(args, val):
    cmd = [args.pan, args.tilt, args.zoom]
    if args.combine_move:
        val = val.split(',')
        if len(val) < 3:
            print("Need pan,tilt and zoom value")
            return
        ptz.send(typeof='absolute', pan=float(
            val[0]), tilt=float(val[1]), zoom=float(val[2]))
    elif args.snapshot:
        ptz.snapShot()
    elif args.get_status:
        ptz.getStatus(output=True)
    elif any(cmd):
        # cmd = [args.pan, args.tilt, args.zoom]
        pan = None
        tilt = None
        zoom = None
        if args.pan:
            pan = float(val)
        elif args.tilt:
            tilt = float(val)
        elif args.zoom:
            zoom = float(val)
        # print(pan, tilt, zoom)
        ptz.send(typeof='absolute', pan=pan, tilt=tilt, zoom=zoom)


def watch_dog(args, val):
    if args.update:
        print("Enter 1 for an hour and 0 for 3 minutes watchdog reset:\n")
        watchdog.run_dog(
            mode=int(val))
    elif args.deactivate:
        watchdog.run_dog(mode=6)
    elif args.sleep:
        print("Enter 2 for an hour and 3 for 3 minutes of sleep:\n")
        watchdog.run_dog(
            mode=int(val))
    else:
        watchdog.run_dog(mode=None)


def cr1000x(args):
    pass


def dts(args):
    pass


def iridium(args):
    pass


def gps(args):
    pass

def device(args):
    if args.running:
        is_on()
    elif args.not_running:
        is_off()
    else: 
        is_on()
        is_off()


def weather(args):
    # call averaging function from vaisala script in avg class - to start long-term data collection
    if args.collect:
        Avg_Reading.average_data()
    # call function to retrieve specific data point from vaisala script in live data class
    elif args.wind_direction:
        Live_Readings.wind_direction()
    elif args.wind_speed:
        Live_Readings.wind_speed()
    elif args.air_temp:
        Live_Readings.air_temperature()
    elif args.humidity:
        Live_Readings.humidity()
    elif args.pressure:
        Live_Readings.pressure()
    elif args.rain_accumulation:
        Live_Readings.rain_accumulation()
    elif args.rain_duration:
        Live_Readings.rain_duration()
    elif args.rain_intensity:
        Live_Readings.rain_intensity()
    elif args.rain_peak_intensity:
        Live_Readings.rain_peak_intensity()
    elif args.hail_accumulation:
        Live_Readings.hail_accumulation()
    elif args.hail_duration:
        Live_Readings.hail_duration()
    elif args.hail_intensity:
        Live_Readings.hail_intensity()
    elif args.hail_peak_intensity:
        Live_Readings.hail_peak_intensity()
    elif args.vaisala_unit:
        Live_Readings.vaisala_unit()
    # show all weather data points if only the weather argument is given
    else:
        Live_Readings.weather_all()


def main():
    """
    Commands group
    Allow easy access to functionalities of the amigos
    """
    # print (args)
    parser, val = args_parser()
    args = parser.parse_args()
    if args.help:
        parser.print_help()
    elif args.schedule == 'power':
        power(args)
    # logic for watchdog configuration
    elif args.schedule == 'watchdog':
        watch_dog(args, val)
    elif args.schedule == 'camera':
        camera(args, val)
    elif args.schedule == 'weather':
        weather(args)
    elif args.schedule == 'device':
        device(args)
    else:
        print('No such a command or it is not implemented yet')
        inp = raw_input("print usage? y/n: ")
        if inp in ['y', 'yes']:
            parser.print_help()


if __name__ == "__main__":
    main()
