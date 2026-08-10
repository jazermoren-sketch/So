import json
import os

FILE = "data/economy.json"


def load_data():

    if not os.path.exists(FILE):
        return {}

    with open(
        FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def save_data(data):

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


def get_player(user_id):

    data = load_data()

    uid = str(user_id)

    if uid not in data:

        data[uid] = {
            "money": 0,
            "xp": 0,
            "level": 1
        }

    return data, uid


def add_money(user_id, amount):

    data, uid = get_player(user_id)

    data[uid]["money"] += amount

    save_data(data)


def get_money(user_id):

    data, uid = get_player(user_id)

    save_data(data)

    return data[uid]["money"]


def add_xp(user_id, amount):

    data, uid = get_player(user_id)

    data[uid]["xp"] += amount

    level_up = False

    need = (
        data[uid]["level"]
        * 100
    )

    while (
        data[uid]["xp"]
        >= need
    ):

        data[uid]["xp"] -= need

        data[uid]["level"] += 1

        level_up = True

        need = (
            data[uid]["level"]
            * 100
        )

    save_data(data)

    return (
        data[uid]["level"],
        data[uid]["xp"],
        level_up
    )


def get_level(user_id):

    data, uid = get_player(user_id)

    save_data(data)

    return (
        data[uid]["level"],
        data[uid]["xp"]
    )