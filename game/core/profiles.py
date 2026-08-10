PROFILES = {}

def get_profile(user_id):

    if user_id not in PROFILES:
        PROFILES[user_id] = {
            "wins": 0,
            "losses": 0,
            "elo": 1000
        }

    return PROFILES[user_id]


def update_win(user_id):
    p = get_profile(user_id)
    p["wins"] += 1
    p["elo"] += 25


def update_loss(user_id):
    p = get_profile(user_id)
    p["losses"] += 1
    p["elo"] -= 15