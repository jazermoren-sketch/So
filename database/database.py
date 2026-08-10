import sqlite3

db = sqlite3.connect(
    "uno.db"
)

cursor = db.cursor()

cursor.execute(
"""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    wins INTEGER DEFAULT 0,
    games INTEGER DEFAULT 0,
    coins INTEGER DEFAULT 0,
    rank_points INTEGER DEFAULT 0
)
"""
)

db.commit()
import sqlite3

db = sqlite3.connect(
    "uno.db"
)

cursor = db.cursor()

cursor.execute(
"""
CREATE TABLE IF NOT EXISTS players(

    user_id INTEGER PRIMARY KEY,

    wins INTEGER DEFAULT 0,

    games INTEGER DEFAULT 0,

    coins INTEGER DEFAULT 0,

    rank_points INTEGER DEFAULT 0,

    streak INTEGER DEFAULT 0
)
"""
)

db.commit()