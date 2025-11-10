import copy
import json
import sys

import yaml

from .. import constants as c
from . import schema
from .methods import directory, git


class Template:
    def __init__(self, **kwargs):
        self.path = kwargs.get("template_path")
        self.filename = kwargs.get("template_filename", c.TEMPLATE_FILENAME)
        self.branch = kwargs.get("branch")
        self.fullpath = None
        self.remote = None
        self.children = []
        self.bus = {}

    def find(self):
        for func in [directory.find, git.find]:
            stop = func(self)
            if stop:
                break
        else:
            sys.exit(f'error: no "{c.TEMPLATE_FILENAME}" file found')

    def read(self):
        with open(self.fullpath, encoding="UTF-8") as fd:
            self.bus = yaml.safe_load(fd)

        # This happens when yaml file is empty.
        if self.bus is None:
            self.bus = {}

    def _reduce(self):
        """
        Reduce to relevant sections.

        This allows a user to add whatever he wants to a scaffold.yml file
        """
        self.bus = {
            "actions": self.bus.get("actions", []),
            "answers": self.bus.get("answers", {}),
            "inherit": self.bus.get("inherit", []),
            "jinja2": self.bus.get("jinja2", {}),
            "questions": self.bus.get("questions", []),
        }

    def _validate(self):
        yaml_schema = yaml.safe_load(schema.SCHEMA)
        validator = schema.LocalValidator(yaml_schema)

        if not validator.validate(self.bus):
            # TODO: flatten to something nice and readable
            locations = str(json.dumps(validator.errors, indent=2))
            raise SystemExit(f"error: YAML schema validation error. Location:\n{locations}") from None

        self.bus = validator.normalized(self.bus)

    def validate(self):
        self._reduce()
        self._validate()

    # pylint: disable=protected-access
    def _recurse(self, root):
        if len(self.bus["inherit"]) == 0:
            return

        # TODO: Recursion detection
        includes = copy.deepcopy(self.bus["inherit"])
        for include in includes:
            path = include["include"]
            filename = include.get("filename")
            branch = include.get("branch")

            tpl = Template(template_path=path, template_filename=filename, branch=branch)
            tpl.find()
            tpl.read()
            tpl.validate()
            tpl._recurse(root)

            tpl._merge_into(root)
            root.bus["templates"] += [{"template_path": path, "template_filename": filename}]

    def recurse(self):
        if len(self.bus["inherit"]) == 0:
            return

        # Backup our bus
        tpl = Template()
        tpl.bus = copy.deepcopy(self.bus)

        # Clear what will be rewritten in the next merge_into
        self.bus["actions"] = []
        self.bus["questions"] = []
        self.bus["answers"] = {}
        self.bus["templates"] = []

        self._recurse(self)
        tpl._merge_into(self)

        # Sort by order if present
        self.bus["questions"] = sorted(self.bus["questions"], key=lambda item: item.get("order", 0))
        self.bus["actions"] = sorted(self.bus["actions"], key=lambda item: item.get("order", 0))

        self.bus["templates"] += [
            {
                "template_path": self.path,
                "template_filename": self.filename,
            },
        ]

    def _merge_into(self, root):
        # Merge questions. "name" must be unique, use it as a key
        dest = {i["name"]: i for i in root.bus["questions"]}
        for question in self.bus["questions"]:
            dest[question["name"]] = question
        dest = [v for k, v in dest.items()]
        root.bus["questions"] = dest

        root.bus["actions"] += self.bus["actions"]
        root.bus["answers"] |= self.bus["answers"]

    def load_answers(self, filepath):
        if not filepath:
            return

        try:
            with open(filepath, encoding="UTF-8") as fd:
                data = yaml.safe_load(fd)
        except Exception as err:
            sys.exit(f"error: failed to open '{filepath}': {err}")

        # TODO: Run answers through jinja
        self.bus["answers"] |= data.get("answers", {})
