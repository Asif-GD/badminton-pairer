import random


# def pair_players(player_list: list[str]):
#     count_of_players = len(player_list)
#
#     if count_of_players <= 4:
#         return pair_4_players(player_list)
#     # elif count_of_players == 5:
#     #     return pair_5_players(player_list)
#     elif count_of_players == 6:
#         return pair_6_players(player_list)
#     # elif count_of_players == 7:
#     #     return pair_7_players(player_list)
#     elif count_of_players == 8:
#         return pair_8_players(player_list)
#     elif 10 <= count_of_players <= 11:
#         return pair_10_or_11_players(player_list)
#     elif count_of_players == 12:
#         return pair_12_players(player_list)
#     else:
#         return "I am unable to comply with this request. Too many players!"


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
    """
    # note: a minor issue, this would flip(reverse) the order in case of 2 or 3 players to be benched.
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

    # this might not be required
    # # if every player has been benched at least once, the cycle starts over.
    # if len(benched_players) == len(player_list):
    #     # -> removes every other player except the player(s) that was benched last turn
    #     if no_of_players_to_be_benched == 1:
    #         benched_players = benched_players[-1:]  # slicing returns a list, so need to wrap it in []
    #     elif no_of_players_to_be_benched == 2:
    #         benched_players = benched_players[-2:]
    #     else:
    #         benched_players = benched_players[-3:]

    random.shuffle(player_list_copy)

    teams = generate_pairs(player_list_copy)

    return teams, benched_players


# def pair_6_players(player_list: list[str]) \
#         -> dict[str, str]:
#     """
#         IMPLEMENTATION: -> no priority. 1 court.
#             - players are paired in random order.
#             - Match 1 -> Team 1 vs. Team 2
#             - Match 2 -> Match 1 winners vs. Team 3
#             - Match 3 -> Match 1 losers vs. Team 3
#             - players are paired again, and so on.
#     """
#     player_list_copy = player_list.copy()
#     random.shuffle(player_list_copy)
#
#     teams = generate_pairs(player_list_copy)
#
#     return teams


def pair_7_players(player_list: list[str]):
    pass


# def pair_8_players(player_list: list[str]) \
#         -> dict[str, str]:
#     """
#         IMPLEMENTATION: -> no priority. 2 courts.
#         - players are paired in random order.
#         - we assume there are two courts available.
#         - at each pairing, a team will play matches against all the other teams.
#     """
#     player_list_copy = player_list.copy()
#     random.shuffle(player_list_copy)
#
#     teams = generate_pairs(player_list_copy)
#
#     return teams


# def pair_10_or_11_players(player_list: list[str]):
#     pass
#
#
def pair_12_players(player_list: list[str]):
    pass
