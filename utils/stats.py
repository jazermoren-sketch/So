import json
import os

FILE = "data/stats.json"


def load_stats():

    if not os.path.exists(FILE):
        return {}

    with open(
        FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def save_stats(data):

    with open(
        FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def get_player(uid):

    data = load_stats()

    uid = str(uid)

    if uid not in data:

        data[uid] = {
            "wins": 0,
            "games": 0,
            "bots": 0,
            "wild": 0,
            "draw4": 0
        }

    return data, uid


def add_win(uid):

    from utils.achievements import (
        check_achievements
    )

    data, uid = get_player(uid)

    data[uid]["wins"] += 1
    data[uid]["games"] += 1

    save_stats(data)

    return check_achievements(
        data[uid]
    )


def add_game(uid):

    data, uid = get_player(uid)

    data[uid]["games"] += 1

    save_stats(data)


def add_bot(uid):

    data, uid = get_player(uid)

    data[uid]["bots"] += 1

    save_stats(data)


def add_wild(uid):

    data, uid = get_player(uid)

    data[uid]["wild"] += 1

    save_stats(data)


def add_draw4(uid):

    data, uid = get_player(uid)

    data[uid]["draw4"] += 1

    save_stats(data)