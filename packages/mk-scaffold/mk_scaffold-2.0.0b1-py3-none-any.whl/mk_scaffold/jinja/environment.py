"""
Jinja2 environment and extensions loading.

Source: https://github.com/cookiecutter/cookiecutter
"""

import sys

from jinja2 import Environment, StrictUndefined
from jinja2.nativetypes import NativeEnvironment


class ExtensionLoaderMixin:
    """
    Mixin providing sane loading of extensions specified in a given context.
    """

    def __init__(self, *_args, context=None, path=None, **kwargs):
        """
        Initialize the Jinja2 Environment object while loading extensions.
        """
        extensions = [
            "jinja2_time.TimeExtension",
        ]

        extensions += context or []

        # Add template path to sys.path for loading
        if path is not None:
            sys.path.append(path)

        try:
            super().__init__(extensions=extensions, **kwargs)
        except ModuleNotFoundError as err:
            sys.exit(f'error: failed to load extensions from "{path}" directory: {err}')


class StrictEnvironment(ExtensionLoaderMixin, Environment):
    """
    Create strict Jinja2 environment.

    Jinja2 environment will raise error on undefined variable in template-
    rendering context.
    """

    def __init__(self, *_args, **kwargs):
        """
        Set the standard Cookiecutter StrictEnvironment.

        Also loading extensions defined in mk-scaffold 'extensions' key.
        """
        super().__init__(**kwargs)
        self.undefined = StrictUndefined


class StrictNativeEnvironment(ExtensionLoaderMixin, NativeEnvironment):
    """
    Create strict Jinja2 environment.

    Jinja2 environment will raise error on undefined variable in template-
    rendering context.
    """

    def __init__(self, *_args, **kwargs):
        """
        Set the standard Cookiecutter StrictEnvironment.

        Also loading extensions defined in mk-scaffold 'extensions' key.
        """
        super().__init__(**kwargs)
        self.undefined = StrictUndefined
