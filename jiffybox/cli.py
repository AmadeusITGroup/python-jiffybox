import json
from operator import attrgetter

import click
from click import echo, echo_via_pager

from .api import JiffyBox
from .format import PlainFormatVisitor

API = None
OUTPUT_FORMAT = None
USE_PAGER = None


def sort_data(data):
    return sorted(data, key=attrgetter('id'))


def format_data(data):
    data = sort_data(data)
    if OUTPUT_FORMAT == 'plain':
        return '\n\n'.join(PlainFormatVisitor().visit(box) for box in data)
    # FIXME id on top in json
    elif OUTPUT_FORMAT == 'json':
        return '\n'.join([json.dumps(elem.json) for elem in data])
    elif OUTPUT_FORMAT == 'json-pretty':
        return '\n'.join([json.dumps(elem.json, indent=2) for elem in data])


def output(data):
    if USE_PAGER:
        echo_via_pager(data)
    else:
        echo(data)


def print_data(data):
    output(format_data(data))


@click.group()
@click.version_option()
@click.option('--api-key',
              envvar='JIFFYBOX_API_KEY',
              help='also read from JIFFYBOX_API_KEY',
              required=True)
@click.option('-v', '--verbose', count=True)
@click.option('--output-format',
              type=click.Choice(['plain', 'json', 'json-pretty']))
@click.option('--pager', is_flag=True)
def jiffybox(api_key, verbose, output_format, pager):
    global API, OUTPUT_FORMAT, USE_PAGER

    API = JiffyBox(api_key=api_key)
    OUTPUT_FORMAT = output_format or 'plain'
    USE_PAGER = pager


@jiffybox.group('box', help='Manages boxes')
def box():
    pass


@box.command('list', help='Lists all boxes in account')
@click.option('--quiet',
              '-q',
              is_flag=True,
              default=False,
              help='Suppress warning at the start')
def list_boxes(quiet):
    if not quiet:
        echo('Please use this API call sparingly; see '
             'https://www.df.eu/fileadmin/user_upload/'
             'jiffybox-api-dokumentation.pdf [pg. 10] for details.',
             err=True)
    print_data(API.boxes())


@box.command('show', help='Shows a single box')
@click.argument('id')
def show_box(id):
    box = API.box(id)
    print_data([box])


@box.command('create', help='Creates and start a new box')
@click.argument('name')
@click.argument('plan')
@click.argument('distribution')
@click.option('--sshkey/--no-sshkey', is_flag=True, default=True)
def create_box(name, plan, distribution, sshkey):
    box = API.create_box(name,
                         plan,
                         distribution=distribution,
                         use_sshkey=sshkey)
    print_data([box])


@box.command('delete', help='Deletes a box')
@click.argument('id')
@click.option('--no-confirm', is_flag=True, default=False)
@click.option('--force', '-f', is_flag=True, help='Stop jiffybox if necessary')
def delete_box(id, no_confirm, force):
    box = API.box(id)
    box_desc = '{0} ({1})'.format(box.id, box.name)

    if not no_confirm:
        click.confirm('Really delete box {}?'.format(box_desc), abort=True)

    echo('Waiting for box to become ready')
    box.wait_for_status()

    if box.running and force:
        echo('Stopping box {}'.format(box_desc))
        box.stop()
        box.wait_for_status()

    if not box.delete():
        raise click.exceptions.RuntimeError('could not delete box')

    echo('Removed box {}'.format(box_desc))


@jiffybox.command(help='Shows a list of distributions')
def distributions():
    print_data(API.distributions())


@jiffybox.command(help='Shows a list of pricing plans')
def plans():
    print_data(API.plans())
