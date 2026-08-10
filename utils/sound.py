import discord


async def play_sound(
    voice,
    file
):

    if voice is None:
        return

    voice.play(
        discord.FFmpegPCMAudio(
            file
        )
    )