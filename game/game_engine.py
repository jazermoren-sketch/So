import asyncio
from game.core.accounts import add_win, add_loss
from ui.game_embed import create_game_embed


class GameEngine:

    def __init__(self, game):
        self.game = game

    async def step(self):

        game = self.game

        if game.finished:
            return

        if game.lock:
            return

        game.lock = True

        try:

            # 🤖 AI / TURN HANDLING
            current = game.current_player

            if current.is_ai:
                await asyncio.sleep(0.4)

            # 🏆 WIN CHECK
            winner = game.winner

            if not winner:
                for p in game.players:
                    if len(p.hand) == 0:
                        winner = p
                        break

            if winner:
                game.finished = True
                game.winner = winner

                # 💰 STATS UPDATE
                for p in game.players:

                    if p.is_ai:
                        continue

                    if p == winner:
                        add_win(p.member.id)
                    else:
                        add_loss(p.member.id)

            # 🎮 UI
            if game.message:
                await game.message.edit(embed=create_game_embed(game))

        finally:
            game.lock = False