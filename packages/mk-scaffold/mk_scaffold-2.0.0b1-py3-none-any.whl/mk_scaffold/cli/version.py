import click

from ..constants import VERSION
from .cli import cli


@cli.command(hidden=True)
def version():
    click.echo(f"mk-scaffold, version {VERSION}")
