import datetime
import sys
import re
import uuid


def print_err():
    pass


def printf(message, date=False):
    """
        Print to the log file
    """
    if date is True:
        with open('/media/mmcblk0p1/logs/system.log', 'a+') as log:
            log.write(message + '\n')
            return
    with open('/media/mmcblk0p1/logs/system.log', 'a+') as log:
        date = str(datetime.datetime.now()) + ': '
        log.write(date + message + '\n')


def amigos_Unit():
    """
    Get the amigos unit ID
    """
    unit = "*Magic*"
    try:
        MAC = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        if MAC.find(":03") != -1:
            unit = "C"
        elif MAC.find(":00") != -1:
            unit = "B"
        elif MAC.find(":05") != -1:
            unit = "A"
    except:
        printf("Failled to get the unit  ``\\_(*_*)_/``")
    return unit


def welcome():
    """Print Welcome message
    """
    unit = amigos_Unit()
    printf("\n" + " "*30 + "*****   *****   *****" + " "*10 + "\n" + " "*20 + "Hi there, I am the Amigos Unit {0} version III.".format(unit) + " "*10 + "\n" +
           " "*10 + "Here, you will find all my actions since I was powered on." + " "*10+"\n" + " "*30 + "*****   *****   *****" + "\n", date=True)
    printf(" "*20 + "If you have any question, please contact my creators", date=True)
    printf(" "*20 + "Theodore Scambos: tascambos@colorado.edu", date=True)
    printf(" "*20 + "Coovi Meha : coovi.meha@colorado.edu", date=True)
    printf(" "*20 + "Bruce Wallin : bruce.wallin@colorado.edu", date=True)
    printf(" "*20 + "Sid Arora : siar7178@colorado.edu", date=True)
    printf(" "*20 + "Ryan Weatherbee : Ryan.Weatherbee@colorado.edu", date=True)
    printf(" "*20 + "Skylar Edwards : sked2869@colorado.edu", date=True)
    printf(" "*20 + "Ema Lyman : barrera@colorado.edu", date=True)
    printf(" "*20 + "Raymie Fotherby : Raymie.Fotherby@colorado.edu", date=True)
    printf(" "*20 + "Timothy White : Timothy.White@colorado.edu", date=True)
    printf(" "*20 + "Jack Soltys : John.Soltys@colorado.edu", date=True)
    printf(" "*20 + "Robert Bauer : robert.bauer@colorado.edu", date=True)
    printf("\n" + " "*30 + "*****   *****   *****" + "\n" +
           " "*10 + "Wait!! please, Give your feedbacks to my creators and keep earth cleaned" + "\n"+" "*30 + "*****   *****   *****" + "\n", date=True)


def sig_handler(signum, frame):
    # save the state here or do whatever you want
    printf('Scheduler has received signal {0}'.format(str(signum)))


def terminateProcess(signalNumber, frame):
    """Last  run before terminating scheduler
    
    Arguments:
        signalNumber {[type]} -- [description]
        frame {[type]} -- [description]
    """
    from monitor import power_consumption
    power = power_consumption()[2]
    printf('received (SIGTERM),  terminating the scheduler. Total power consumed is {0}'.format(
        str(power)[0:-6]))
    sys.exit(0)
