"""
Ask questions and answer them by prompting the user

Special cases to be handled:
- ctrl-d: Set value to None

"""

import sys

from prompt_toolkit import prompt as user_input
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.validation import ValidationError, Validator

from .. import utils
from .validators import allowed, max_length, min_length, nullable, vartype

bindings = KeyBindings()


def _eval_string(condition, env, ctx):
    if not isinstance(condition, str):
        return condition
    return env.from_string(condition).render(**ctx)


def validate(value, schema):
    """
    Validate the answer and return modified answer if needed.

    Return value + stop (True/False)
    """
    # Order matters. By checking nullable and default first
    # we can make assumptions on values (null? not null? etc.)
    validators = [
        vartype,
        nullable,
        allowed,
        max_length,
        min_length,
        # min_value TODO
        # max_value TODO
    ]

    # Returns (value, True) if we are to stop iterating,
    # we are to replace value by a new value
    for validator in validators:
        value, stop = validator.validate(value, schema)
        if stop is True:
            return value
    return value


# pylint: disable=redefined-outer-name
def stdin_input(prompt):
    """
    Convenience function in order to be mocked
    """
    return input(prompt)


# pylint: disable=redefined-outer-name
def _prompt(question, env, ctx):
    """
    Ask the question until it is answered or canceled

    Returns key, value
    """
    # Get question details
    name = question["name"]
    prompt = question["prompt"] + ": "
    description = question.get("description")
    description = _eval_string(description, env, ctx)
    schema = question.get("schema", {})

    # if hidden, then return default, which is the value
    # in answer, and if missing, the default from scaffold.yml
    hidden = question.get("hidden", False)
    hidden = _eval_string(hidden, env, ctx)
    hidden = utils.string_as_bool(hidden)

    default = schema.get("default")

    def prevalidate(x, schema):
        # Exceptions are raised
        validate(x, schema)
        return True

    validator = Validator.from_callable(lambda x: prevalidate(x, schema))

    while True:
        try:
            if hidden:
                answer = schema.get("default")
            elif sys.stdin.isatty():
                kwargs = {}
                if default:
                    kwargs["default"] = default

                # TODO: yes_no_dialog
                answer = user_input(
                    prompt,
                    validator=validator,
                    bottom_toolbar=description,
                    key_bindings=bindings,
                    validate_while_typing=False,
                    **kwargs,
                )
            else:
                answer = stdin_input(prompt)
            answer = validate(answer, schema)
            return name, answer

        except EOFError:
            # ctrl-d was used
            try:
                answer, _ = validate(None, schema)
                return name, answer
            except ValidationError:
                continue


def prepare(question, answers, env, ctx):
    """
    Determine if the question is to be asked, and
    if so, build a prompt

    Return true if question is to be asked.
    """
    # Get question details
    name = question["name"]
    schema = question.get("schema", {})

    # Will we prompt this question?
    condition = question.get("if")
    condition = _eval_string(condition, env, ctx)
    if condition is not None:
        question["if"] = condition
        if not condition:
            return False

    # Set the answer as the default, override if necessary
    # It will be eval just under
    answer = (answers or {}).get(question["name"])
    if answer is not None:
        schema["default"] = str(answer)

    # Prepare the default value
    # pylint: disable=redefined-outer-name
    default = schema.get("default")
    default = _eval_string(default, env, ctx)
    if default is not None:
        schema["default"] = str(default)

    # Build prompt
    prompt = _eval_string(name, env, ctx)
    question["prompt"] = str(prompt)
    return True


# pylint: disable=redefined-outer-name
def prompt(env, ctx, tpl):
    """
    For every question in the input file, ask the question
    and record the answer in the context

    Fills in `questions`
    """
    answers = tpl.bus["answers"]

    for question in tpl.bus["questions"]:
        if not prepare(question, answers, env, ctx):
            continue

        name, answer = _prompt(question, env, ctx)
        question["value"] = answer
        ctx["scaffold"][name] = answer
    return ctx
