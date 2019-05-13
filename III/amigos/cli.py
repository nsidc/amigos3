# -*- coding: utf-8 -*-
import threading
import os.path
import amigos.argparse as argparse
import amigos.monitor
import amigos.peripheral
from amigos.schedules import setup

my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "text.txt")


def main():
    """
    Commands group
    Allow easy access to vital functionality of the amigos
    """

    parser = argparse.ArgumentParser(prog='Amigos', add_help=False)
    # Group or command for schedule viewing
    schedule = parser.add_argument_group('Schedule', 'Show all the schedules')
    schedule.add_argument(
        'schedule', help='View all pending schedule', nargs='?')
    schedule.add_argument(
        '-s', '--summer', help='View summer schedule', action='store_true')
    schedule.add_argument(
        '-w', '--winter', help='View winter schedule', action='store_true')

    # group of command for weather viewing
    weather = parser.add_argument_group('weather', 'show weather data')
    weather.add_argument('weather', help='View all data saved', nargs='?')
    weather.add_argument('-a', help='Show actual weather', action='store_true')

    # group of command for watchdog configureting
    wdog = parser.add_argument_group('Watchdog', 'Change watch dog setup')
    wdog.add_argument('watchdog', help='View running watchdog setting', nargs='?')
    wdog.add_argument('-u', '--update',
                      help='update the watchdog cycle', action='store_true')
    wdog.add_argument('-d', '--deactivate',
                      help='deactivate watchdog from auto update', action='store_true')

    # power commands
    power = parser.add_argument_group('Watchdog', 'Change watch dog setup')
    power.add_argument('power', help='View running watchdog setting', nargs='?')
    power.add_argument('-r_on', '--router_on',
                       help='Router on', action='store_true')
    power.add_argument('-r_off', '--router_off',
                       help='Router off', action='store_true')
    power.add_argument('-g_on', '--gps_on',
                       help='GPS on', action='store_true')
    power.add_argument('-g_off', '--gps_off',
                       help='GPS off', action='store_true')
    # help command
    h = parser.add_argument_group('Help', 'show help menu')
    h.add_argument('-h', '--help',
                   help='Show this menu', action='store_true')

    # retrieve all arguments enter
    args = parser.parse_args()
    # print (args)

    if args.help:
        parser.print_help()

    # logic for watchdog configuration
    elif args.schedule == 'watchdog':
        sp = setup()
        if args.update:
            sp.watchdog(arg=int(input("Enter 1 for an hour and .5 for 3 minutes:\n")))
        elif args.deactivate:
            sp.watchdog(arg="deactivate")
    elif args.schedule == 'power':
        sp = setup()
        command = (args.router_on, args.router_off, args.gps_on, args.gps_off)
        if any(command):
            sp.power(command)
        else:
            print "Too few argument. No device specified."


if __name__ == "__main__":
    main()
