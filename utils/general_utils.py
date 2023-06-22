import random

def randomize_list(lst):
    randomized_list = lst.copy()  # Make a copy of the original list
    random.shuffle(randomized_list)
    return randomized_list