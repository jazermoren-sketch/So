import asyncio
from ui.game_embed import create_game_embed
from game.ai import play_ai


class UnoEngine:

    async def start(self, session):
        session.data["started"] = True

    async def step(self, session):

        if session.finished:
            return

        if session.lock:
            return

        session.lock = True

        try:

            current = session.current_player

            # 🤖 AI TURN
            if current.is_ai:
                await asyncio.sleep(0.4)
                await play_ai(session)

            # 🏆 WIN CHECK
            for p in session.players:
                if len(p.hand) == 0:
                    session.finished = True
                    session.winner = p

            # 🎮 UI UPDATE
            if session.message:
                await session.message.edit(
                    embed=create_game_embed(session)
                )

        finally:
            session.lock = False