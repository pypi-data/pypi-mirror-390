import atexit
import os
import shutil
import subprocess
import sys
import tempfile

from ... import constants as c
from . import directory


def _get_git():
    retval = shutil.which("git")
    if retval is None:
        print('warning: "git" executable was not found', file=sys.stderr)
    return retval


def _get_tmpdir():
    """
    Create a temporary folder to be deleted at exit
    """
    tmpdir = tempfile.mkdtemp(prefix="scaffold")

    def remove_tmpdir():
        shutil.rmtree(tmpdir)

    atexit.register(remove_tmpdir)
    return tmpdir


def _clone(tpl):
    git = _get_git()
    tmpdir = _get_tmpdir()

    # Prepare the command line that depends on local
    # or remote
    cmdline = [git, "clone"]
    cmdline += ["--single-branch"]
    if tpl.branch:
        cmdline += ["--branch", tpl.branch]
    if os.path.exists(tpl.path) and os.path.isdir(tpl.path):
        # This is a local repository and git prefers with the
        # "file://"
        tpl.path = f"file://{tpl.path}"
    else:
        cmdline += ["--depth", "1"]
    cmdline += [tpl.path, "repository"]

    try:
        subprocess.run(cmdline, cwd=tmpdir, check=True)
    except subprocess.CalledProcessError:
        sys.exit(f'error: failed to clone remote repository "{tpl.path}"')

    tpl.remote = tpl.path
    tpl.path = os.path.join(tmpdir, "repository")
    return directory.verify(tpl)


def find(tpl):
    """
    path can be a remote git+ssh, or git+http, or even a local path
    if branch is None, we checkout the default branch, usually main or master
    """
    # If path starts with file://, then skip it
    if tpl.path.startswith(c.SCHEMA_FILE):
        return False

    return _clone(tpl)
