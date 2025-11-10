from prompt_toolkit.validation import ValidationError


def validate(value, schema):
    """
    Return { value to use, stop (True/False) }

    If stop is True, the rest of the validators are skipped.
    """
    allowed = schema.get("allowed")
    if allowed is None:
        return value, False

    if value not in allowed:
        allowed = ", ".join(allowed)
        raise ValidationError(message=f"Answer must be within [{allowed}]")

    return value, False
