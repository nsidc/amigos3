# -*- coding: utf-8 -*-
import threading
import os.path
import click
import amigos.monitor
import amigos.peripheral
from amigos.schedules import print_sched

sh = print_sched()
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "text.txt")


def runnable():
    """
    Main function that run in the background start of the
    amigos system
    """
    pass


@click.group(invoke_without_command=True)
@click.option("-s", '--schedules', help="get schedules", default='')
@click.pass_context
def main(ctx, schedules: str):
    """
    Commands group
    Allow easy access to vital functionality of the amigos
    """
    pass


@main.command()
def summer():
    """
    View running schedules  for summer
    """
    click.echo(click.style('Loading summer schedule!', fg='green'))
    with open(path) as f:
        content = str(f.readlines())
        content = eval(content)
        for cont in content:
            print("* {}".format(cont))


@main.command()
def winter():
    """
    View running schedules  for winter
    """
    click.echo(click.style('Loading winter schedule!', fg='green'))
    with open(path) as f:
        content = str(f.readlines())
        content = eval(content)
        for cont in content:
            print("* {}".format(cont))


if __name__ == "__main__":
    main()
