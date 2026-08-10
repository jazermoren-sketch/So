import asyncio


async def start_uno_timer(
    game,
    player
):

    await asyncio.sleep(5)

    if game.finished:
        return

    if len(player.hand) != 1:
        return

    if player.said_uno:
        return

    player.draw(
        game.deck,
        2
    )

    name = (
        player.name
        if player.is_ai
        else player.member.mention
    )

    if game.message:

        await game.message.channel.send(
            f"🚨 {name} نسي UNO (+2)"
        )