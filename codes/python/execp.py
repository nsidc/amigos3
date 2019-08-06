import functools
import datetime
import sys

# def catch_exceptions(cancel_on_failure=False):
#     def catch_exceptions_decorator(job_func):
#         @functools.wraps(job_func)
#         def wrapper(*args, **kwargs):
#             try:
#                 return job_func(*args, **kwargs)
#             except:
#                 import traceback
#                 print(traceback.format_exc())
#                 if cancel_on_failure:
#                     return schedule.CancelJob
#         return wrapper
#     return catch_exceptions_decorator


def print_err():
    pass


def set_reschedule(device):
    with open("/media/mmcblk0p1/logs/reschedule.log", "w+") as res:
        res.write(device)


def printf(message, date=False):
    """
        Print to the log file
    """
    if date == True:
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
    try:
        ifconfig = None
        with open("/root/ifconfig.txt", 'r') as f:
            ifconfig = f.read()
        if ifconfig.find("70:B3:D5:65:46:03") != -1:
            return "C"
        elif ifconfig == "":
            pass
        elif ifconfig == "":
            pass
    except:
        printf("Failled to get the unit  ``\\_(^/)_/``")


def welcome():
    unit = amigos_Unit()
    printf("\n" + " "*30 + "*****   *****   *****" + " "*10 + "\n" + " "*20 + "Hi there, I am the Amigos Unit {0} version III.".format(unit) + " "*10 + "\n" +
           " "*10 + "Here, you will find all my actions since I was powered on." + " "*10+"\n" + " "*30 + "*****   *****   *****" + "\n", date=True)
    printf(" "*20 + "If you have any question, please contact my creators", date=True)
    printf(" "*20 + "Theodore Scambos: tascambos@colorado.edu", date=True)
    printf(" "*20 + "Coovi Meha : coovi.meha@colorado.edu", date=True)
    printf(" "*20 + "Bruce Wallin : bruce.wallin@colorado.edu", date=True)
    printf(" "*20 + "Sid Aurora : siar7178@colorado.edu", date=True)
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
    printf('received (SIGTERM),  terminating the scheduler. System must be going down or a human sends "kill" command.')
    sys.exit(0)
