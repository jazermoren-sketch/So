import asyncio
from game.core.profiles import update_win, update_loss
from ui.game_embed import create_game_embed


class GameEngine:

    def __init__(self, game):
        self.game = game
        self.running = False

    async def start(self):
        self.running = True
        await self.loop()

    async def loop(self):

        while self.running and not self.game.finished:

            await asyncio.sleep(0.7)

            await self.step()

    async def step(self):

        game = self.game

        if game.lock:
            return

        game.lock = True

        try:

            current = game.current_player

            # 🤖 AI TURN
            if current.is_ai:
                from game.ai import play_ai
                await play_ai(game)

            # 🏆 WIN CHECK
            winner = game.check_winner()

            if winner:

                game.finished = True
                self.running = False

                # 💰 UPDATE STATS
                for p in game.players:

                    if p.is_ai:
                        continue

                    if p == winner:
                        update_win(p.member.id)
                    else:
                        update_loss(p.member.id)

                await game.message.channel.send(
                    f"🏆 Winner: {winner.name if winner.is_ai else winner.member.mention}"
                )

            # 🎮 UI UPDATE
            if game.message:
                await game.message.edit(
                    embed=create_game_embed(game)
                )

        finally:
            game.lock = False