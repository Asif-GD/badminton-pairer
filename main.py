import random
from itertools import combinations


def pair_players(player_list: list[str]):  # dict[int,list[str]]

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


def pair_4_players(player_list: list[str]):
    random.shuffle(player_list)

    teams = list()
    # combinations() returns possible combinations in order
    for team in combinations(player_list, 2):
        teams.append(team)

    count: int = 1
    first_index: int = 0
    second_index: int = len(teams) - 1
    while first_index < second_index:
        print(f"Match {count}: {teams[first_index]} vs. {teams[second_index]}")
        count += 1
        first_index += 1
        second_index -= 1


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

    # generate_pairs()
    team_number: int = 1
    for i in range(0, len(player_list_copy), 2):
        print(f"Team: {team_number}")
        print(f"{player_list_copy[i]} , {player_list_copy[i + 1]}")
        team_number += 1

    print(f"Benched player -> {player_to_be_benched}")


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
    """
        IMPLEMENTATION: -> since there are 7 players, one player a.k.a. lucky_player will play 2 matches in succession
        lucky_player will be paired with 2nd player and the seventh_player, in team 1 and team 4 respectively.
        lucky_player -> will be retrieved from db.
        lucky_player will become the seventh_player for next pairing as he would have played two matches consecutively.
        note: a lucky_player list is maintained to ensure everyone gets fair number of games in a session.
    """
    lucky_player_list: list[str] = list()
    lucky_player: str = str()
    seventh_player: str = str()
    team_number: int = 1

    # lucky_player_list = ["Rahul"]
    # lucky_player_list = ["Rahul", "Asif", "Mahesh", "Shiva", "Dinesh", "Rajiv", "Ankit"]

    player_list_copy = player_list.copy()

    # if every player has been a lucky_player at least once, the cycle starts over.
    if len(lucky_player_list) == len(player_list):
        # print("inside if")
        lucky_player_list = lucky_player_list[-2:len(lucky_player_list)]

    elif len(lucky_player_list) < len(player_list):
        # print("inside elif")
        lucky_player = random.choice(player_list_copy)

        # to ensure every player gets to be lucky_player at least once
        while lucky_player in lucky_player_list:
            lucky_player = random.choice(player_list_copy)

        lucky_player_list.append(lucky_player)

    lucky_player = lucky_player_list[-1]
    player_list_copy.remove(lucky_player)

    # usually, in case of first pairing
    if len(lucky_player_list) == 1:
        seventh_player = random.choice(player_list_copy)
        player_list_copy.remove(seventh_player)
    else:
        """
            we need the lucky_player from the previous pairing
            -1 -> holds the lucky_player of this pairing
            -2 -> holds the lucky_player of previous pairing
        """
        seventh_player = lucky_player_list[-2]
        player_list_copy.remove(seventh_player)

    # the lucky_player and seventh_player positions have to be preserved for proper pairings
    random.shuffle(player_list_copy)
    player_list_copy.insert(0, lucky_player)
    player_list_copy.append(seventh_player)

    # print(f"lucky_player_list -> {lucky_player_list}")
    # print(f"lucky_player -> {lucky_player}")
    # print(f"seventh_player -> {seventh_player}")
    # print(f"player_list_copy -> {player_list_copy}")

    for i in range(0, len(player_list_copy), 2):
        print(f"Team: {team_number}")
        if team_number != 4:
            print(f"{player_list_copy[i]} , {player_list_copy[i + 1]}")
        else:
            print(f"{seventh_player} , {lucky_player}")
        team_number += 1


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


player_list_4 = ["Asif", "Rahul", "Mahesh", "Shiva"]
player_list_5 = ["Asif", "Rahul", "Mahesh", "Shiva", "Dinesh"]
player_list_6 = ["Asif", "Rahul", "Mahesh", "Shiva", "Dinesh", "Rajiv"]
player_list_7 = ["Asif", "Rahul", "Mahesh", "Shiva", "Dinesh", "Rajiv", "Ankit"]
player_list_8 = ["Asif", "Rahul", "Mahesh", "Shiva", "Dinesh", "Rajiv", "Ankit", "Ravi"]

# pair_players(player_list_4)
# pair_players(player_list_5)
# pair_players(player_list_6)
pair_players(player_list_7)
# pair_players(player_list_8)
