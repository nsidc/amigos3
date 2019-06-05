# -*- coding: utf-8 -*-
import threading
import os.path
import amigos.argparse as argparse
import amigos.watchdog as watchdog
import amigos.gpio as gpio

my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "text.txt")


def main():
    """
    Commands group
    Allow easy access to vital functionality of the amigos
    """

    parser = argparse.ArgumentParser(prog='Amigos', add_help=False)
    # Group or command for schedule viewing
    schedule = parser.add_argument_group(
        'Set or View Schedules', 'Show all the schedules'
    )
    schedule.add_argument('schedule', help='View all pending schedule', nargs='?')
    schedule.add_argument(
        '-s', '--summer', help='View summer schedule', action='store_true'
    )
    schedule.add_argument(
        '-w', '--winter', help='View winter schedule', action='store_true'
    )

    # group of command for weather viewing
    weather = parser.add_argument_group('Read weather', 'show weather data')
    weather.add_argument('weather', help='View all data saved', nargs='?')
    weather.add_argument('-a', help='Show actual weather', action='store_true')

    # group of command for watchdog configureting
    wdog = parser.add_argument_group('Set Watchdog', 'Change watch dog setup')
    wdog.add_argument('watchdog', help='View running watchdog setting', nargs='?')
    wdog.add_argument(
        '-u', '--update', help='update the watchdog cycle', action='store_true'
    )
    wdog.add_argument('-sl', '--sleep', help='Put board to sleep', action='store_true')
    wdog.add_argument(
        '-d',
        '--deactivate',
        help='deactivate watchdog from auto update',
        action='store_true',
    )

    # power commands
    power = parser.add_argument_group('Power Control', 'Control power on gpio pins')
    power.add_argument(
        'power', help='Need one of the secondary arguments bellow', nargs='?'
    )
    power.add_argument('-r_on', '--router_on', help='Router on', action='store_true')
    power.add_argument('-r_off', '--router_off', help='Router off', action='store_true')
    power.add_argument('-g_on', '--gps_on', help='GPS on', action='store_true')
    power.add_argument('-g_off', '--gps_off', help='GPS off', action='store_true')
    power.add_argument(
        '-w_on', '--weather_on', help='Weather station on', action='store_true'
    )
    power.add_argument(
        '-w_off', '--weather_off', help='Weather station off', action='store_true'
    )
    power.add_argument(
        '-off', '--power_off', help='power down all peripherals', action='store_true'
    )
    power.add_argument(
        '-on', '--power_on', help='power up all peripherals', action='store_true'
    )

    camera = parser.add_argument_group(
        'Control Camera', 'Control camera position, take pictures and more'
    )
    camera.add_argument('camera', help='required a secondary command', nargs='?')
    camera.add_argument('-up', '--move_up', help='Move camera up', action='store_true')
    camera.add_argument(
        '-up', '--move_up', help='Move camera down', action='store_true'
    )
    camera.add_argument(
        '-left', '--move_left', help='Move camera to the left', action='store_true'
    )
    camera.add_argument(
        '-right', '--move_right', help='Move camera to the right', action='store_true'
    )

    # help command
    h = parser.add_argument_group('Help', 'show help menu')
    h.add_argument('-h', '--help', help='Show this menu', action='store_true')

    # retrieve all arguments entered
    args = parser.parse_args()
    # print (args)
    if args.help:
        parser.print_help()

    # logic for watchdog configuration
    elif args.schedule == 'watchdog':
        if args.update:
            watchdog.set_mode(
                mode=int(
                    input("Enter 1 for an hour and 0 for 3 minutes watchdog reset:\n")
                )
            )
        elif args.deactivate:
            watchdog.set_mode(default=True)
        elif args.sleep:
            watchdog.set_mode(
                mode=int(input("Enter 2 for an hour and 3 for 3 minutes of sleep:\n"))
            )
        else:
            watchdog.set_mode(mode=None)
    elif args.schedule == 'power':
        command = (args.router_on, args.router_off, args.gps_on, args.gps_off)
        if args.weather_on:
            gpio.weather_on(1)
        elif args.weather_off:
            gpio.weather_off(1)
        elif args.power_down:
            gpio.power_down(1)
        elif args.power_up:
            gpio.power_up(1)
        elif any(command):
            gpio.router_on(int(args.router_on))
            gpio.router_off(int(args.router_off))
            gpio.gps_on(int(args.gps_on))
            gpio.gps_off(int(args.gps_off))
        else:
            print("Too few arguments. No device specified.")
    else:
        print('No such a command or it is not implemented yet')
        inp = raw_input("print usage? y/n: ")
        if inp in ['y', 'yes']:
            parser.print_help()


if __name__ == "__main__":
    main()
