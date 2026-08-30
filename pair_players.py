import random


def generate_pairs(player_list: list[str]) \
        -> dict[str, str]:
    team_number: int = 1
    pairs: dict[str, str] = dict()
    for i in range(0, len(player_list), 2):
        pairs[str(team_number)] = f"{player_list[i]}, {player_list[i + 1]}"
        team_number += 1

    return pairs


def pair_4_6_or_8_players(player_list: list[str]) \
        -> dict[str, str]:
    """
            IMPLEMENTATION: -> no priority.
                - players are paired in random order.
    """
    player_list_copy = player_list.copy()
    random.shuffle(player_list_copy)

    teams = generate_pairs(player_list_copy)

    return teams


def pair_5_9_10_or_11_players(player_list: list[str], benched_player_list: list[str]) \
        -> tuple[dict[str, str], list[str]]:
    """
        IMPLEMENTATION:
            - bench a random player not already in benched_players this cycle;
                reset when everyone's had a turn.
            - in case of
                5 or 9 players -> 1 player is benched
                10 players -> 2 players are benched
                11 players -> 3 players are benched
            - the remaining four players are paired at random.
    """

    benched_players = benched_player_list.copy()

    # set number of players to be benched
    """
    - in case of
        5 or 9 players -> 1 player is benched
        10 players -> 2 players are benched
        11 players -> 3 players are benched
    """
    no_of_players_to_be_benched = len(player_list) % 4

    """
    - we ensure that the len(benched_players) does not exceed the len(player_list)
    - why? we have set that when every one is benched at least once, the cycle starts over.
    - in case of 11 players, since 3 players are to be benched, at 4th iteration that logic would break. 
    note: a minor issue, this would flip(reverse) the order in case of 2 or 3 players to be benched.
        - because the player to be benched is chosen at random.
    - an alternate implementation was to simply clear the benched_players list;
        except for the players that were benched the previous turn
    - but that would mean the order at which the players were benched gets completely tossed out. 
    """
    while len(player_list) - len(benched_players) < no_of_players_to_be_benched:
        benched_players.pop(0)

    player_list_copy = player_list.copy()

    while no_of_players_to_be_benched != 0:
        player_to_be_benched = random.choice(player_list)

        # to ensure every player gets benched at least once
        while player_to_be_benched in benched_players:
            player_to_be_benched = random.choice(player_list)

        benched_players.append(player_to_be_benched)
        player_list_copy.remove(player_to_be_benched)

        no_of_players_to_be_benched -= 1

    random.shuffle(player_list_copy)

    teams = generate_pairs(player_list_copy)

    return teams, benched_players


def pair_7_players(player_list: list[str], lucky_player_list: list[str], seventh_player: str) \
        -> tuple[dict[str, str], list[str], str]:
    """
        IMPLEMENTATION:
            - since there are 7 players, one player a.k.a. lucky_player will play 2 matches in succession
            - lucky_player will be paired with 2nd player and the seventh_player,
                in team 1 and team 4 respectively.
            - the lucky_player will become the seventh_player for next pairing
                as he would have played two matches consecutively.
            - lucky_player & seventh_player will be retrieved from db.
            - a lucky_player list is maintained to ensure everyone gets fair number of games in a session.
    """
    player_list_copy = player_list.copy()
    lucky_players: list[str] = lucky_player_list.copy()

    """
    - if every player has been a lucky_player at least once, the cycle starts over.
    - the very first player in the lucky_players list becomes the lucky player again in this pairing.
    - else, a random player becomes a lucky player
    """
    if len(lucky_players) == len(player_list):
        lucky_player_this_pairing = lucky_players.pop(0)

    else:
        lucky_player_this_pairing = random.choice(player_list_copy)

        # to ensure every player gets to be lucky_player at least once
        while lucky_player_this_pairing in lucky_player_list:
            lucky_player_this_pairing = random.choice(player_list_copy)

    lucky_players.append(lucky_player_this_pairing)
    player_list_copy.remove(lucky_player_this_pairing)

    seventh_player: str = seventh_player
    if not seventh_player:  # -> usually in case of first pairing
        seventh_player = random.choice(player_list_copy)
    player_list_copy.remove(seventh_player)

    """
    - the lucky_player and seventh_player positions have to be preserved for proper pairings
    - the lucky_player_this_pairing is inserted twice, at the start and at the end of the list
        to prevent generate_pairs() from running into list index out of range error.
    """
    random.shuffle(player_list_copy)
    player_list_copy.insert(0, lucky_player_this_pairing)
    player_list_copy.append(seventh_player)
    player_list_copy.append(lucky_player_this_pairing)

    teams = generate_pairs(player_list_copy)

    # after the teams are generated, the lucky_player_this_pairing becomes seventh_player for next pairing
    seventh_player = lucky_player_this_pairing

    return teams, lucky_players, seventh_player


def pair_12_players(player_list: list[str]):
    pass
