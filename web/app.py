from flask import Flask, render_template
from game.core.profiles import PROFILES

app = Flask(__name__)


@app.route("/")
def home():

    leaderboard = sorted(
        PROFILES.items(),
        key=lambda x: x[1]["elo"],
        reverse=True
    )

    return render_template(
        "index.html",
        leaderboard=leaderboard
    )


@app.route("/player/<user_id>")
def player(user_id):

    data = PROFILES.get(user_id)

    if not data:
        return "Player not found"

    return render_template(
        "player.html",
        user_id=user_id,
        data=data
    )


def run_web():
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )