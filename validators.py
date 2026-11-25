import re
from typing import Final

# Check A -> reading the pattern left to right
# [A-Za-z0-9_]+ -> accepts one or more of letters, digits or underscore, nothing else.
# for example,
#   invalid name -> "José"
#   valid name -> "john", "john_doe"
ALLOWED_CHAR_PATTERN: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9_]+")

# Check B -> reading the pattern left to right
# [A-Za-z0-9]+ -> first part of the name; can be chars (more than 1) of english alphabets (both cases) and numbers.
# (?: ... ) -> an optional part.
# _[A-Za-z0-9]+ -> similar to first part, but it starts with a '_' and this part is optional.
# So, a name must start with an alphabet or a number and if it has a second part, the second must begin with an
#   underscore followed by alphabets or numbers.
# for example,
#   invalid names -> leading "_abc", trailing "abc_", doubled "a__b", or just "___"
#   valid names -> "abc", "abc_def"
NAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9]+(?:_[A-Za-z0-9]+)?")


def validate_player_name(name: str) -> str:
    """
        Validates the player names against preset rules
            - names should be of length 3 to 30 characters
            - cannot be empty
            - no white spaces allowed (beginning, trailing, or in the middle)
            - names are of format
                -> single name (or)
                -> firstname_lastname
            - no special characters allowed, except underscore.

    :param name: Player's name.
    :return: Player's name after validation, capitalized.
    :raises ValueError: If any of the above rules are violated.
    """

    # cannot be empty
    if not name:  # -> checks for ''
        raise ValueError("Player name cannot be empty.")

    # no white spaces allowed (beginning, trailing, or in the middle)
    elif any(ch.isspace() for ch in name):
        raise ValueError(
            f"Name: '{name}' must not contain any whitespace. Please use a player's first name or "
            f"use the format of 'firstname'_'lastname'."
        )

    # names should be of length 3 to 30 characters
    elif not 3 <= len(name) <= 30:
        raise ValueError(f"Name '{name}' must be between 3 to 30 characters long.")

    # check A: every character must come from the allowed set.
    # runs first, so that if it passes, any later failure can only be about underscores.
    elif not ALLOWED_CHAR_PATTERN.fullmatch(name):
        raise ValueError(
            f"Name '{name}' contains invalid characters. Only letters, numbers and an "
            f"underscore are allowed."
        )

    # check B: the characters are fine, a failure here must be underscore placement.
    # this check covers cases like "_bob", "bob_", "a__b" and "a_b_c".
    elif not NAME_PATTERN.fullmatch(name):
        raise ValueError(
            f"'{name}' is an invalid format. A name must be a single name (e.g. 'john') "
            f"or two parts separated by one underscore (e.g. 'john_doe')."
        )

    # in case user entered john_doe -> John_Doe, alex -> Alex
    name: str = '_'.join(part.capitalize() for part in name.split('_'))

    return name


def normalize_and_check_duplicates(players: list[str]) -> list[str]:
    """
        Validates the players' name individually using validate_player_name();
        then checks for duplicate names in the player list sent by the user.

    :param players: The list of players' names.
    :return: The list of players' names, after validation.
    :raises ValueError: If there are duplicate entries.
    """
    # checks for all per-name rules (length, whitespace, allowed characters, capitalization)
    validated_names: list[str] = [validate_player_name(name) for name in players]

    # rejects case-insensitive duplicate names
    if len(set(validated_names)) != len(validated_names):  # -> set() doesn't support duplicate values.
        raise ValueError("Players names must be unique (case-insensitive).")

    return validated_names
