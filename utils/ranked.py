PLAYER_RANKS = {}


def add_rank(user_id, amount):

    if user_id not in PLAYER_RANKS:
        PLAYER_RANKS[user_id] = 0

    PLAYER_RANKS[user_id] += amount

    if PLAYER_RANKS[user_id] < 0:
        PLAYER_RANKS[user_id] = 0

    return PLAYER_RANKS[user_id]


def get_rank(user_id):

    return PLAYER_RANKS.get(
        user_id,
        0
    )