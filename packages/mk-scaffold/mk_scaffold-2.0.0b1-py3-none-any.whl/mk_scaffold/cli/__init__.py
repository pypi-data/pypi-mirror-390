# pragma: exclude file
# pylint: disable=redefined-builtin
from . import cli, clone, help, version


def main():
    cli.cli()
