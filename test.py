import random
from operator import index
from traceback import print_tb

from main import *

player_list_4 = ["Asif", "Rahul", "Mahesh", "Shiva"]
player_list_6 = ["Asif", "Rahul", "Mahesh", "Shiva", "Dinesh", "Rajiv"]

# """
# checking shuffle()
# """
# print(f"Before shuffle/re-order: {player_list_4}")
#
# # shuffle players using random.shuffle()
# random.shuffle(player_list_4)
# print(f"After shuffle: {player_list_4}")

# """
# # reorder players using random.choice()
# """
# player_list_4_copy = player_list_4.copy()
# reordered_player_list = list()
# for count in range(len(player_list_4)):
#     random_player = random.choice(player_list_4_copy)
#     reordered_player_list.append(random_player)
#     player_list_4_copy.remove(random_player)
#
# print(f"After reorder: {reordered_player_list}")

# player_map = dict()
# print(player_list_4)
# player_list_4_copy = player_list_4.copy()
# for count in range(1, len(player_list_4) + 1):
#     random_player = random.choice(player_list_4_copy)
#     player_map[random_player] = count
#     player_list_4_copy.remove(random_player)
#
# print(player_map)

"""
Checking 6 player combinations
"""
# print(f"{player_list_6} \n")
# six_player_combination = combinations(player_list_6, 2)
# #  combinations twice doesn't work in a way I want
# # pairs = combinations(six_player_combination,2)
# for item in six_player_combination:
#     print(item)

"""
testing if list subtraction is possible
"""
# list_subtraction = player_list_6 - player_list_4  # -> doesn't work
# print(list_subtraction)

"""
testing skip in range()
"""
# for i in range(0, 7, 2):
#     print(i)

"""
testing 8-player combinations
"""
# # player_list_8 = ["Asif", "Rahul", "Mahesh", "Shiva", "Dinesh", "Rajiv", "Ankit", "Ravi"]
# player_list_8 = ["1", "2", "3", "4", "5", "6", "7", "8"]
# eight_player_combination = combinations(player_list_8, 2)  # -> returns an itertools.combinations object
# # print(eight_player_combination)
#
# # itertools.combinations object gets destroyed after it is unpacked by the below operation
# # for item in eight_player_combination:
# #     print(item)
#
# comb_list = list(eight_player_combination)  # -> an empty list now if eight_player_combination was unpacked
#
# for index in range(len(comb_list)):  # -> this does nothing if comb_list is []
#     print(f"{index} -> {comb_list[index]}")
# # print(comb_list)
# # print(len(comb_list))

"""
testing list reassignment
"""
# random_list: list[int] = [1, 2, 3, 4, 5]
# print(f"Before reassignment: -> {random_list}")
#
# random_list = [random_list[-1]] # -> -1 points to the last element in list
# print(f"After reassignment: -> {random_list}")

"""
testing create_session_id
"""
# def create_session_id(username: str, player_list: list[str]) -> str:
#     session_id: str = username
#     for player in player_list:
#         for index in range(0, 3):
#             session_id += player[index]
#
#     return session_id
#
#
# print(player_list_4)
# print(create_session_id(username="username", player_list=player_list_4))
# print(player_list_6)
# print(create_session_id(username="username", player_list=player_list_6))

"""
testing string <-> list conversion
"""
# sample_string = "['1_Asif', '2_Violet', '3_Indigo', '4_Blue', '5_Yellow']"
# sample_list = ['1_Asif', '2_Violet', '3_Indigo', '4_Blue', '5_Yellow']
#
# sample_string_2 = str(sample_list)
# print(sample_string_2)
#
# sample_string_2 += "[6_Orange]"
# print(sample_string_2)
#
# print(list(sample_string))
