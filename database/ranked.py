from database.database import (
    db,
    cursor
)


def add_rank(
    uid,
    points
):

    cursor.execute(
        """
        UPDATE players
        SET rank_points=
        rank_points+?
        WHERE user_id=?
        """,
        (
            points,
            uid
        )
    )

    db.commit()