import cloup

from ..constants import VERSION


@cloup.group(invoke_without_command=True, no_args_is_help=True)
@cloup.version_option(VERSION)
def cli():
    pass
