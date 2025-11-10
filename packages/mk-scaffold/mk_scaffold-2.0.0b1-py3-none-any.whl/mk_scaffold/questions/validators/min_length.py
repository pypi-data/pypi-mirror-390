from prompt_toolkit.validation import ValidationError


def validate(value, schema):
    """
    Return { value to use, stop (True/False) }

    If stop is True, the rest of the validators are skipped.
    """
    vartype = schema.get("type", "string")
    if vartype != "string":
        return value, False

    min_length = schema.get("min_length", None)
    if min_length and len(value) < min_length:
        raise ValidationError(message=f"Answer cannot be shorter than {min_length} characters") from None
    return value, False
