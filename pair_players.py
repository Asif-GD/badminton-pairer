import random
from itertools import combinations


def pair_players(player_list: list[str]):
    count_of_players = len(player_list)

    if count_of_players <= 4:
        print("Next time, decide on pairs yourselves; you indecisive bums! :p")
        return pair_4_players(player_list)
    elif count_of_players == 5:
        return pair_5_players(player_list)
    elif count_of_players == 6:
        return pair_6_players(player_list)
    elif count_of_players == 7:
        return pair_7_players(player_list)
    elif count_of_players == 8:
        return pair_8_players(player_list)
    elif 9 <= count_of_players <= 11:
        return pair_9_to_11_players(player_list)
    elif count_of_players == 12:
        return pair_12_players(player_list)
    else:
        return "I am unable to comply with this request. Too many players!"


def generate_pairs(player_list: list[str]) -> dict[str, str]:
    team_number: int = 1
    pairs: dict[str, str] = dict()
    for i in range(0, len(player_list), 2):
        pairs.update({f"Team: {team_number}": f"{player_list[i]} , {player_list[i + 1]}"})
        team_number += 1

    return pairs


def pair_4_players(player_list: list[str]):
    """
            IMPLEMENTATION: -> no priority. 1 court.
                - players are paired in random order.
    """
    player_list_copy = player_list.copy()
    random.shuffle(player_list_copy)

    teams = generate_pairs(player_list_copy)

    return teams


def pair_5_players(player_list: list[str]):
    """
        IMPLEMENTATION: -> when there are players with priority
            - if there are players (usually 1) who were benched the previous game, they'd be given priority.
            - one player from the previous match will be chosen at random and benched.
            - the remaining four players are paired at random.

        IMPLEMENTATION: -> no players in priority (usually, the first pairing)
            - one player will be chosen and benched, randomly.
            - the player who was benched will be given priority in the next pairing, and so on.
    """

    benched_player: list[str] = list()

    # if every player has been benched at least once, the cycle starts over.
    if len(benched_player) == len(player_list):
        benched_player = [benched_player[-1]]

    player_list_copy = player_list.copy()
    player_to_be_benched = random.choice(player_list)

    # to ensure every player gets benched at least once
    while player_to_be_benched in benched_player:
        player_to_be_benched = random.choice(player_list)

    benched_player.append(player_to_be_benched)
    player_list_copy.remove(player_to_be_benched)

    random.shuffle(player_list_copy)

    teams = generate_pairs(player_list_copy)
    teams.update({f"Benched player": f"{player_to_be_benched}"})

    return teams


def pair_6_players(player_list: list[str]):
    """
        IMPLEMENTATION: -> no priority. 1 court.
            - players are paired in random order.
            - Match 1 -> Team 1 vs. Team 2
            - Match 2 -> Match 1 winners vs. Team 3
            - Match 3 -> Match 1 losers vs. Team 3
            - players are paired again, and so on.
    """
    random.shuffle(player_list)

    # generate_pairs()
    team_number: int = 1
    for i in range(0, len(player_list), 2):
        print(f"Team: {team_number}")
        print(f"{player_list[i]} , {player_list[i + 1]}")
        team_number += 1


def pair_7_players(player_list: list[str]):
    pass


def pair_8_players(player_list: list[str]):
    """
        IMPLEMENTATION: -> no priority. 2 courts.
        - players are paired in random order.
        - we assume there are two courts available.
        - at each pairing, a team will play matches against all the other teams.
    """
    random.shuffle(player_list)

    team_number: int = 1
    for i in range(0, len(player_list), 2):
        print(f"Team: {team_number}")
        print(f"{player_list[i]} , {player_list[i + 1]}")
        team_number += 1


def pair_9_to_11_players(player_list: list[str]):
    pass


def pair_12_players(player_list: list[str]):
    pass
