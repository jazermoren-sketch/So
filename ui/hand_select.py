import traceback
import discord
import asyncio

from ui.game_embed import create_game_embed
from ui.wild_view import WildView
from game.ai import play_ai
from game.uno_timer import start_uno_timer


try:
    from utils.ranked import add_rank
except:
    def add_rank(uid, amount):
        return 0


try:
    from battlepass.xp import add_xp
except:
    def add_xp(uid, xp):
        return (0, 0)


try:
    from battlepass.rewards import get_reward
except:
    def get_reward(level):
        return None


class HandSelect(discord.ui.Select):

    def __init__(self, game, player):

        self.game = game
        self.player = player

        options = []

        for i, card in enumerate(player.hand):
            options.append(
                discord.SelectOption(
                    label=str(card),
                    value=str(i)
                )
            )

        if not options:
            options.append(
                discord.SelectOption(
                    label="لا توجد أوراق",
                    value="0"
                )
            )

        super().__init__(
            placeholder="اختر ورقة",
            min_values=1,
            max_values=1,
            options=options
        )

    async def reward_players(
        self,
        interaction,
        winner
    ):

        for player in self.game.players:

            if player.is_ai:
                continue

            try:

                level_before, _ = add_xp(
                    player.member.id,
                    0
                )

                level_after, _ = add_xp(
                    player.member.id,
                    50
                )

                if level_after > level_before:

                    await interaction.channel.send(
                        f"🎫 {player.member.mention} وصل للمستوى {level_after}"
                    )

                    reward = get_reward(
                        level_after
                    )

                    if reward:
                        await interaction.channel.send(
                            f"🎁 {player.member.mention} حصل على {reward['name']}"
                        )

                if player == winner:

                    rp = add_rank(
                        player.member.id,
                        25
                    )

                    await interaction.channel.send(
                        f"🏆 {player.member.mention} +25 RP ({rp})"
                    )

                else:

                    rp = add_rank(
                        player.member.id,
                        -10
                    )

                    await interaction.channel.send(
                        f"📉 {player.member.mention} -10 RP ({rp})"
                    )

            except:
                pass

    async def finish_game(
        self,
        interaction,
        winner
    ):

        self.game.finished = True
        self.game.winner = winner

        try:
            await self.reward_players(
                interaction,
                winner
            )
        except:
            pass

        if winner.is_ai:
            name = winner.name
        else:
            name = winner.member.mention

        from ui.game_view import GameView

        embed, file = create_game_embed(
            self.game
        )

        await self.game.message.edit(
            embed=embed,
            attachments=[file],
            view=GameView(
                self.game
            )
        )

        await interaction.channel.send(
            f"🏆 الفائز هو {name}"
        )

        try:
            from bot import games
            games.pop(interaction.channel.id, None)
        except Exception:
            pass

    async def callback(
        self,
        interaction
    ):

        try:

            await interaction.response.defer(
                ephemeral=True
            )

            if self.game.finished:
                return

            current = self.game.current_player

            if current.is_ai:

                return await interaction.followup.send(
                    "❌ دور البوت.",
                    ephemeral=True
                )

            if current.member.id != interaction.user.id:

                return await interaction.followup.send(
                    "❌ ليس دورك.",
                    ephemeral=True
                )

            index = int(
                self.values[0]
            )

            if index >= len(
                self.player.hand
            ):
                return

            card = self.player.hand[index]

            valid = (

                card.color == self.game.current_color

                or

                card.value == self.game.current_card.value

                or

                card.color == "wild"
            )

            if not valid:

                return await interaction.followup.send(
                    "❌ لا يمكن لعب هذه الورقة.",
                    ephemeral=True
                )

            # حذف الورقة
            self.player.hand.pop(index)

            # إعادة UNO
            self.player.said_uno = False

            # إذا بقات ورقة وحدة
            if len(self.player.hand) == 1:

                asyncio.create_task(
                    start_uno_timer(
                        self.game,
                        self.player
                    )
                )

            self.game.current_card = card

            # WILD
            if card.color == "wild":

                async def done(
                    interaction,
                    color
                ):

                    self.game.current_color = color

                    winner = self.game.check_winner()

                    if winner:

                        return await self.finish_game(
                            interaction,
                            winner
                        )

                    if card.value == "wild4":
                        self.game.draw_four()
                    else:
                        self.game.next_turn()

                    from ui.game_view import GameView

                    embed, file = create_game_embed(
                        self.game
                    )

                    await self.game.message.edit(
                        embed=embed,
                        attachments=[file],
                        view=GameView(
                            self.game
                        )
                    )

                    await play_ai(
                        self.game
                    )

                    embed, file = create_game_embed(
                        self.game
                    )

                    await self.game.message.edit(
                        embed=embed,
                        attachments=[file],
                        view=GameView(
                            self.game
                        )
                    )

                return await interaction.followup.send(
                    "🎨 اختر اللون",
                    view=WildView(
                        self.game,
                        done
                    ),
                    ephemeral=True
                )

            self.game.current_color = card.color

            winner = self.game.check_winner()

            if winner:

                return await self.finish_game(
                    interaction,
                    winner
                )

            if card.value == "skip":

                self.game.skip()

            elif card.value == "reverse":

                self.game.reverse()

            elif card.value == "draw2":

                self.game.draw_two()

            elif card.value == "wild4":

                self.game.draw_four()

            else:

                self.game.next_turn()

            from ui.game_view import GameView

            embed, file = create_game_embed(
                self.game
            )

            await self.game.message.edit(
                embed=embed,
                attachments=[file],
                view=GameView(
                    self.game
                )
            )

            await interaction.followup.send(
                f"✅ لعبت {card}",
                ephemeral=True
            )

            await play_ai(
                self.game
            )

            embed, file = create_game_embed(
                self.game
            )

            await self.game.message.edit(
                embed=embed,
                attachments=[file],
                view=GameView(
                    self.game
                )
            )

        except Exception:

            print(
                "=== ERROR ==="
            )

            traceback.print_exc()