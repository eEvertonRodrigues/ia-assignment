import random


def random_tiebreak(candidates, maximizing_player):
    best_value = max(value for _, value in candidates) if maximizing_player else min(value for _, value in candidates)
    return random.choice([child for child, value in candidates if value == best_value])
