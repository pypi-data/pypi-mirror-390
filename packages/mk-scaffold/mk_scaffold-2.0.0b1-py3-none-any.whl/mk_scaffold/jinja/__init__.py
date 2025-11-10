from datetime import datetime
from pathlib import Path

from .environment import StrictNativeEnvironment


def get(tpl):
    # jinja context, everything of ours is "scaffold".* based
    # globals are set at the root
    ctx = {
        "scaffold": {},
        "day": datetime.now().day,
        "month": datetime.now().month,
        "year": datetime.now().year,
        "curdir": str(Path.cwd()),
    }

    # Get user options for jinja from questions file.
    opts = tpl.bus.get("jinja2", {})

    env = StrictNativeEnvironment(**opts)
    return env, ctx
