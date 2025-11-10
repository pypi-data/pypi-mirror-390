from prompt_toolkit.validation import ValidationError

from ... import utils


def validate(value, schema):
    """
    Return { value to use, stop (True/False) }

    If stop is True, the rest of the validators are skipped.
    """
    # ctrl-d gives us a None
    if value is None:
        return None, False

    vartype = schema.get("type", "string")
    if vartype == "string":
        value = str(value)

    if vartype == "integer":
        try:
            value = int(value)
        except ValueError:
            raise ValidationError(message="Invalid type. Expected an integer") from None

    if vartype == "boolean":
        try:
            value = utils.string_as_bool(value)
            return value, True
        except ValueError:
            raise ValidationError(message="Invalid type. Expected a boolean") from None

    return value, False
