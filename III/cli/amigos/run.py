import threading
import click
import amigos.monitor
import amigos.peripheral
from amigos.schedules import print_sched
sh = print_sched()

if __name__ == "__main__":
    sh.start_task()
