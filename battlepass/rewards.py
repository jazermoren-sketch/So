REWARDS = {

    5: {
        "coins": 500,
        "name": "500 Coins"
    },

    10: {
        "coins": 1000,
        "name": "1000 Coins"
    },

    15: {
        "coins": 2000,
        "name": "2000 Coins"
    },

    20: {
        "title": "👑 King",
        "name": "King Title"
    },

    30: {
        "title": "💎 Diamond",
        "name": "Diamond Title"
    }
}


def get_reward(level):

    return REWARDS.get(level)