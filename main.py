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

    benched_player = list()
    count: int = 1

    while count <= len(player_list):
        player_list_copy = player_list.copy()
        player_to_be_benched = random.choice(player_list)

        # to ensure every player gets benched at least once
        while player_to_be_benched in benched_player:
            player_to_be_benched = random.choice(player_list)

        benched_player.append(player_to_be_benched)
        player_list_copy.remove(player_to_be_benched)

        random.shuffle(player_list_copy)

        print("------------------")
        print(f"\t Match {count}: \t")
        print("------------------")
        for number in range(len(player_list)):
            if number == len(player_list) - 1:
                print(f"{player_to_be_benched} -> Benched")
            else:
                print(f"{player_list_copy[number]} -> {number + 1}")

        count += 1


def pair_6_players(player_list: list[str]):
    """
        IMPLEMENTATION: -> when there are players with priority
            - if there are players who were benched the previous game, they'd be given priority.
            - two players from the previous match will be chosen and paired with players in priority, randomly.
            - the remaining two players are benched and will be given priority in the next pairing, and so on.

        IMPLEMENTATION: -> no players in priority (usually, the first pairing)
            - two players will be chosen and benched, randomly.
            - the two players who are benched will be given priority in the next pairing, and so on.
    """
    priority_players = list()
    benched_players = list()
    # priority_players = ["Mahesh", "Shiva"]

    if priority_players:
        players_without_priority = player_list.copy()
        for player in priority_players:
            players_without_priority.remove(player)

        while len(priority_players) != 4:
            random_player = random.choice(players_without_priority)
            priority_players.append(random_player)
            players_without_priority.remove(random_player)

        benched_players = players_without_priority.copy()

    else:
        priority_players = player_list.copy()
        while len(benched_players) != 2:
            random_player = random.choice(priority_players)
            benched_players.append(random_player)
            priority_players.remove(random_player)

    random.shuffle(priority_players)

    for number in range(0, 4):
        print(f"{priority_players[number]} -> {number + 1}")

    for player in benched_players:
        print(f"{player} -> benched")

    priority_players = benched_players.copy()
    # print(priority_players)


def pair_7_players(player_list: list[str]):
    """
        IMPLEMENTATION: -> since there are 7 players, one player a.k.a. ace_player will play 2 matches
        ace_player will be paired with 2nd player and the 7th player, in team 1 and team 4 respectively.
        ace_player -> will be retrieved from db.
        note: an ace_player list is maintained to ensure everyone gets fair number of games in a session.
    """
    ace_players = list()
    team_number: int = 1
    # ace_player = ["Rahul"]
    # ace_player = ["Rahul", "Asif", "Mahesh", "Shiva", "Dinesh", "Rajiv", "Ankit"]

    if len(ace_players) == 7:
        # print("inside if")
        ace_players.clear()

    random.shuffle(player_list)
    ace_players.append(player_list[0])

    for i in range(0, len(player_list), 2):
        print(f"Team: {team_number}")
        if i != 6:
            print(f"{player_list[i]} , {player_list[i + 1]}")
        else:
            print(f"{player_list[i]} , {player_list[0]}")
        team_number += 1


def pair_8_players(player_list: list[str]):
    """
        IMPLEMENTATION: ->
        We assume there are two courts available.
        At each pairing, a team will play matches against all the other teams.
    """
    team_number: int = 1
    random.shuffle(player_list)
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
# pair_players(player_list_7)
pair_players(player_list_8)
