from prompt_toolkit.validation import ValidationError


def validate(value, schema):
    """
    Return { value to use, stop (True/False) }

    If stop is True, the rest of the validators are skipped.
    """
    vartype = schema.get("type", "string")
    if vartype != "string":
        return value, False

    max_length = schema.get("max_length", None)
    if max_length and len(value) > max_length:
        raise ValidationError(message=f"Answer cannot be longer than {max_length} characters") from None
    return value, False
