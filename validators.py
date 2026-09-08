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
    :raises ValueError: if any of the above rules are violated.
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

    # no special characters allowed, except underscore.
    elif not all(ch.isalnum() or ch == "_" for ch in name):
        raise ValueError(
            f"Name '{name}' contains invalid characters. Only letters, numbers, and a single "
            f"underscore separator (e.g. 'firstname_lastname') are allowed."
        )

    return name.capitalize()



