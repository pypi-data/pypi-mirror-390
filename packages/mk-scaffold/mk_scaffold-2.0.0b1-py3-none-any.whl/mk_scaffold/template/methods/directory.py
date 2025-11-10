import os
import sys
from pathlib import Path

from ... import constants as c


def verify(tpl):
    """
    Use args to search within a directory for the file "scaffold.yml", or filename
    passed in args.

    Returns break/continue value
    """

    # If path starts with file://, then remove it
    if tpl.path.startswith(c.SCHEMA_FILE):
        tpl.path = tpl.path[len(c.SCHEMA_FILE) :]

    if os.path.isfile(tpl.path):
        sys.exit("error: positional argument should point to a directory, or remote git repository, and not a file")

    fullpath = os.path.join(tpl.path, tpl.filename)
    if not os.path.isfile(fullpath):
        return False

    # Ensure that fullpath is relative to tpl.path
    real_fullpath = os.path.realpath(fullpath)
    real_tplpath = os.path.realpath(tpl.path)
    if not Path(real_fullpath).is_relative_to(real_tplpath):
        sys.exit(f'error: File "{tpl.filename}" is not relative to the template path')

    tpl.fullpath = fullpath
    return True


def find(tpl):
    """
    Search for a directory with the file "scaffold.yml", or filename
    passed in args.
    """

    # If branch is specified, don't look for a local
    # directory, but return to force git handler
    if tpl.branch:
        return False

    return verify(tpl)
