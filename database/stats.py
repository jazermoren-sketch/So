from database.database import (
    db,
    cursor
)


def create_user(uid):

    cursor.execute(
        """
        INSERT OR IGNORE
        INTO players(
            user_id
        )
        VALUES(?)
        """,
        (
            uid,
        )
    )

    db.commit()


def add_win(uid):

    create_user(uid)

    cursor.execute(
        """
        UPDATE players
        SET wins=wins+1,
            games=games+1
        WHERE user_id=?
        """,
        (
            uid,
        )
    )

    db.commit()