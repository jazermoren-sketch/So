import json
import os

FILE = "data/battlepass.json"


def load_pass():

    if not os.path.exists(FILE):
        return {}

    with open(
        FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def save_pass(data):

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


def add_xp(user_id, xp):

    data = load_pass()

    user_id = str(user_id)

    if user_id not in data:

        data[user_id] = {
            "xp": 0,
            "level": 1
        }

    data[user_id]["xp"] += xp

    while (
        data[user_id]["xp"]
        >=
        data[user_id]["level"] * 100
    ):

        data[user_id]["xp"] -= (
            data[user_id]["level"] * 100
        )

        data[user_id]["level"] += 1

    save_pass(data)

    return (
        data[user_id]["level"],
        data[user_id]["xp"]
    )


def get_pass(user_id):

    data = load_pass()

    user_id = str(user_id)

    if user_id not in data:

        return (
            1,
            0
        )

    return (
        data[user_id]["level"],
        data[user_id]["xp"]
    )