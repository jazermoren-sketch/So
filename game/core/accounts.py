ACCOUNTS = {}

def get_user(user_id):

    if user_id not in ACCOUNTS:
        ACCOUNTS[user_id] = {
            "wins": 0,
            "losses": 0,
            "xp": 0,
            "rank": 1000
        }

    return ACCOUNTS[user_id]


def add_win(user_id):
    user = get_user(user_id)
    user["wins"] += 1
    user["xp"] += 50
    user["rank"] += 25


def add_loss(user_id):
    user = get_user(user_id)
    user["losses"] += 1
    user["rank"] -= 10