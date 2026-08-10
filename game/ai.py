import asyncio

from ui.game_embed import create_game_embed


async def play_ai(game):

    if game.finished:
        return

    if game.ai_running:
        return

    game.ai_running = True

    try:

        colors = {
            "red": "🔴",
            "green": "🟢",
            "blue": "🔵",
            "yellow": "🟡"
        }

        while (
            not game.finished
            and game.current_player.is_ai
        ):

            ai = game.current_player

            print("AI TURN:", ai.name)

            await asyncio.sleep(2)

            played = False

            for i, card in enumerate(ai.hand):

                valid = (
                    card.color == game.current_color
                    or card.value == game.current_card.value
                    or card.color == "wild"
                )

                if not valid:
                    continue

                played = True

                ai.hand.pop(i)

                game.current_card = card

                if card.color == "wild":

                    counter = {
                        "red": 0,
                        "green": 0,
                        "blue": 0,
                        "yellow": 0
                    }

                    for c in ai.hand:
                        if c.color in counter:
                            counter[c.color] += 1

                    chosen = max(counter, key=counter.get)

                    game.current_color = chosen

                    if game.message:
                        await game.message.channel.send(
                            f"{ai.name} لعب 🃏 واختار {colors[chosen]}"
                        )

                else:

                    game.current_color = card.color

                winner = game.check_winner()

                if winner:

                    game.finished = True
                    game.winner = winner

                    if game.message:

                        from ui.game_view import GameView

                        embed, file = create_game_embed(game)

                        await game.message.edit(
                            embed=embed,
                            attachments=[file],
                            view=GameView(game)
                        )

                        if winner.is_ai:
                            name = winner.name
                        else:
                            name = winner.member.mention

                        await game.message.channel.send(
                            f"🏆 الفائز هو {name}"
                        )

                    return

                if card.value == "skip":
                    game.skip()

                elif card.value == "reverse":
                    game.reverse()

                elif card.value == "draw2":
                    game.draw_two()

                elif card.value == "wild4":
                    game.draw_four()

                else:
                    game.next_turn()

                break

            if not played:

                ai.draw(game.deck, 1)

                card = ai.hand[-1]

                can_play = (
                    card.color == game.current_color
                    or card.value == game.current_card.value
                    or card.color == "wild"
                )

                if can_play:
                    continue

                game.next_turn()

            if game.message:

                from ui.game_view import GameView

                embed, file = create_game_embed(game)

                await game.message.edit(
                    embed=embed,
                    attachments=[file],
                    view=GameView(game)
                )

    except Exception:
        import traceback
        traceback.print_exc()

    finally:
        game.ai_running = False