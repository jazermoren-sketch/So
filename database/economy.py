from database.database import (
    db,
    cursor
)


def add_coins(
    uid,
    amount
):

    cursor.execute(
        """
        UPDATE players
        SET coins=
        coins+?
        WHERE user_id=?
        """,
        (
            amount,
            uid
        )
    )

    db.commit()