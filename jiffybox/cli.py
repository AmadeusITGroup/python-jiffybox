import json
from operator import attrgetter

import click
from click import echo, echo_via_pager

from .api import JiffyBox


API = None
OUTPUT_FORMAT = None
USE_PAGER = None


def sort_data(data):
    return sorted(data, key=attrgetter('id'))


def format_data(data):
    data = sort_data(data)
    if OUTPUT_FORMAT == 'plain':
        for elem in data:
            echo('id: ' + str(elem.id))
            for attr in elem._attributes.keys():
                echo('  ' + attr + ': ' + str(getattr(elem, attr)))

    # FIXME id on top in json
    elif OUTPUT_FORMAT == 'json':
        return '\n'.join([json.dumps(elem.json) for elem in data])
    elif OUTPUT_FORMAT == 'json-pretty':
        return '\n'.join([json.dumps(elem.json, indent=True) for elem in data])


def output(data):
    if USE_PAGER:
        echo_via_pager(data)
    else:
        echo(data)


def print_data(data):
    output(format_data(data))


@click.group()
@click.version_option()
@click.option('--api-key', envvar='JIFFYBOX_API_KEY',
              help='also read from JIFFYBOX_API_KEY',
              required=True)
@click.option('-v', '--verbose', count=True)
@click.option('--output-format', type=click.Choice(['plain', 'json',
                                                    'json-pretty']))
@click.option('--pager', is_flag=True)
def jiffybox(api_key, verbose, output_format, pager):
    global API, OUTPUT_FORMAT, USE_PAGER

    API = JiffyBox(api_key=api_key)
    OUTPUT_FORMAT = output_format or 'plain'
    USE_PAGER = pager


@jiffybox.group('box')
def box():
    pass


@box.command('list')
@click.confirmation_option(prompt='This may take some time')
def list_boxes():
    print_data(API.boxes())


@box.command('show')
@click.argument('id')
def show_box(id):
    box = API.box(id)
    print_data([box])


@box.command('create')
@click.argument('name')
@click.argument('plan')
@click.argument('distribution')
@click.option('--sshkey/--no-sshkey', is_flag=True, default=True)
def create_box(name, plan, distribution, sshkey):
    box = API.create_box(name, plan, distribution=distribution,
                         use_sshkey=sshkey)
    print_data([box])


@jiffybox.command()
def distributions():
    print_data(API.distributions())


@jiffybox.command()
def plans():
    print_data(API.plans())
