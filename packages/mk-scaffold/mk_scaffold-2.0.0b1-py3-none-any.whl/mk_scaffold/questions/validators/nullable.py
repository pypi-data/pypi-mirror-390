from prompt_toolkit.validation import ValidationError


def validate(value, schema):
    """
    Return { value to use, stop (True/False) }

    If stop is True, the rest of the validators are skipped.
    """
    # ctrl-d gives us a None, if value is not None,
    # we're not concerned
    if value is not None:
        return value, False

    nullable = schema.get("nullable", False)
    if nullable:
        return None, True
    raise ValidationError(message="Answer is required")
