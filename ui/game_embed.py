import discord


def create_game_embed(game):

    embed = discord.Embed(
        title="🎮 UNO Game",
        color=0x00ff00
    )

    # البطاقة الحالية
    embed.add_field(
        name="🃏 Current Card",
        value=str(game.current_card),
        inline=False
    )

    # اللون الحالي
    colors = {
        "red": "🔴 أحمر",
        "green": "🟢 أخضر",
        "blue": "🔵 أزرق",
        "yellow": "🟡 أصفر"
    }

    current_color = colors.get(
        game.current_color,
        "⚫ Wild"
    )

    embed.add_field(
        name="🎨 Current Color",
        value=current_color,
        inline=False
    )

    # الدور
    current = game.current_player

    if current.is_ai:
        turn = current.name
    else:
        turn = current.member.mention

    embed.add_field(
        name="⏳ Turn",
        value=turn,
        inline=False
    )

    # صورة البطاقة
    file = None

    try:

        file = discord.File(
            game.current_card.image,
            filename="card.png"
        )

        embed.set_image(
            url="attachment://card.png"
        )

    except Exception:

        pass

    return embed, file