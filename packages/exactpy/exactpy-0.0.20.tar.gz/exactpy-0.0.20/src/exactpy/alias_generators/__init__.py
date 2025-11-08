import re


def special_snake_to_pascal(snake: str) -> str:
    """Converting to snake case, will lead to loss
    of information in the case of two-or-more letter
    acronyms, of which the most well known example is:
    ID (pascal) -> id (pascal)

    MSDN limits capitalization of acronyms to two letters
    in Pascal case, but the Exact Online API models
    capitalize the full acronym, no matter the length.

    This will cause issues converting back to Pascal,
    as we don't know anymore which letters form acronyms.
    For this purpose, we need a special delimiter to modify
    snake case in such a way we can still discover these
    acronyms. That delimiter is a double underscore `__`,
    and is used in the following way. Consider the string
    'RFIDTag', which would become 'rfid_tag' in snake case.
    In the new syntax, this becomes, 'rfid__tag'. The double
    underscore indicates that the entire previous section
    should be capitalized when converting back to Pascal.

    A special case is id, which will always become ID even
    without the use of underscores. Other standalone two
    letter acronyms will have to be suffixed with `__` as well.

    Args:
        snake (str): The "special" snake cased string.

    Returns:
        str: A (non-standard / Exact Online compatible) Pascal cased string.
    """

    # Special case for id, because it's extremely common
    if snake == "id":
        return "ID"

    pascal = snake.title()

    # First convert the acronyms using special delimiter
    pascal = re.sub(
        "([0-9A-Za-z]+)__(?=[0-9A-Z]*)",
        lambda m: m.group(1).upper(),
        pascal,
    )

    # Regular snake case conversion
    pascal = re.sub(
        "([0-9A-Za-z])_(?=[0-9A-Z])",
        lambda m: m.group(1),
        pascal,
    )

    return pascal
