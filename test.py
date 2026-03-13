import random

from main import *

player_list_4 = ["Asif", "Rahul", "Mahesh", "Shiva"]
player_list_6 = ["Asif", "Rahul", "Mahesh", "Shiva", "Dinesh", "Rajiv"]

print(f"Before shuffle/re-order: {player_list_4}")

# shuffle players using random.shuffle()
random.shuffle(player_list_4)
print(f"After shuffle: {player_list_4}")

# reorder players using random.choice()
player_list_4_copy = player_list_4.copy()
reordered_player_list = list()
for count in range(len(player_list_4)):
    random_player = random.choice(player_list_4_copy)
    reordered_player_list.append(random_player)
    player_list_4_copy.remove(random_player)

print(f"After reorder: {reordered_player_list}")

# pairs = []
# for item in pair_4_players(player_list_4):
#     print(item)
# pairs.append(item)

# print(pairs)
# random.shuffle(player_list_4)
# print(player_list_4)
# for item in combinations(player_list_4, 2):
#     print(item)
#     pairs.append(item)
#
# print(pairs)

# for item in combinations(pairs, 2):
#     print(item)

# map_item = map(random.choice(player_list_4), count())
# print(map_item)

# print(random.choice(player_list_4))

# player_map = dict()
# print(player_list_4)
# for count in range(1, len(player_list_4) + 1):
#     print(f"count: {count}")
#     player_list_4_copy = player_list_4
#     player_map[count] = random.choice(player_list_4_copy)
#     player_list_4_copy.remove(player_map[count])
#
# print(player_map)
