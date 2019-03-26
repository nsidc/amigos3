# -*- coding: utf-8 -*-
import threading
import click
import amigos.monitor
import amigos.peripheral
from amigos.schedules import print_sched

sh = print_sched()


def runnable():
    """
    Main function that run in the background start of the
    amigos system
    """
    pass


@click.group(invoke_without_command=True)
@click.option("-s", '--schedules', help="Summer Schedule", default='')
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
    View running schedules
    """
    click.echo(click.style('Loading summer schedule!', fg='green'))
    with open('text.txt') as f:
        content = str(f.readlines())
        content = eval(content)
        for cont in content:
            print("* {}".format(cont))


@main.command()
def winter():
    click.echo(click.style('Loading winter schedule!', fg='green'))
    with open('text.txt') as f:
        content = str(f.readlines())
        content = eval(content)
        for cont in content:
            print("* {}".format(cont))


if __name__ == "__main__":
    main()
