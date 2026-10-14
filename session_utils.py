import hashlib


def create_session_id(username: str, player_list: list[str], digest_size: int = 8) -> str:
    """
        Creates a session_id to be stored as part of the user record in the db.
        IMPLEMENTATION:
            - a session_id is unique, so the player_list is always sorted to prevent duplicates.
            - the username, all the players names from the user's list of registered players
                are joined using a delimiter '|'.
            - the entire string is encoded as utf-8.
            - after encoding , it is hashed using hashlib.blake2s with digest_size=8.
            - the hash is then converted back to str using hexdigest()

    :param username: The username of the user registering retrieved using the discord bot.
    :param player_list: The list of players being registered under user.
    :param digest_size: The length of the hash.
    :return: A string of size N.
    """
    session_id: str

    # 1. sorted independently of the caller,
    #       so, session_id stays correct even if a future caller passes an unsorted list
    sorted_player_list: list[str] = sorted(player_list)

    # 2. format -> username + players' names (joined by |)
    #       adding a delimiter between names to prevent collision;
    #       ["ab", "c"] and ["a", "bc"] both become "abc" and can collide
    joined_sorted_player_list: str = username + "|" + "|".join(sorted_player_list)

    # 3. hash functions work on bytes, not str, so it has to be encoded;
    #       encoding with utf-8 so the result stays platform independent
    data: bytes = joined_sorted_player_list.encode("utf-8")

    # 4. hashing using blake2s with digest_size of 8 bytes
    hash_data: hashlib.blake2s = hashlib.blake2s(data, digest_size=digest_size)

    # 5. hexdigest() gives a str, 2 hex characters per byte -> digest_size=8 gives 16 characters;
    #       alternatively, digest() would give raw bytes
    session_id = hash_data.hexdigest()

    return session_id
