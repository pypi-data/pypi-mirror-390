import click

from .cli import cli


# pylint: disable=redefined-builtin
@cli.command(hidden=True)
@click.pass_context
def help(ctx):
    click.echo(cli.get_help(ctx))
