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
    # priority_players =list()
    pass


def pair_7_players(player_list: list[str]):
    pass


def pair_8_players(player_list: list[str]):
    pass


def pair_9_to_11_players(player_list: list[str]):
    pass


def pair_12_players(player_list: list[str]):
    pass


player_list_4 = ["Asif", "Rahul", "Mahesh", "Shiva"]
player_list_5 = ["Asif", "Rahul", "Mahesh", "Shiva", "Dinesh"]
player_list_6 = ["Asif", "Rahul", "Mahesh", "Shiva", "Dinesh", "Rajiv"]

# pair_players(player_list_4)
# pair_players(player_list_5)
