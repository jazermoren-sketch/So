import asyncio
import threading

import discord
from discord.ext import commands

from game.uno_game import UnoGame
from ui.game_view import GameView
from ui.game_embed import create_game_embed
from application.application import ApplicationCommands
from application.messages import MessageListener
from application.sendstage import SendStage
from application.addquestion import AddQuestion
from application.editquestion import EditQuestion
from application.removequestion import RemoveQuestion
from application.listquestions import ListQuestions

from web.app import run_web
import json
import os
from discord import app_commands

TOKEN = "YOUR_BOT_TOKEN"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

games = {}


class LobbyView(discord.ui.View):

    def __init__(self, host):
        super().__init__(timeout=None)

        self.host = host
        self.players = [host]
        self.message = None
        self.seconds = 15

    def make_embed(self):

        embed = discord.Embed(
            title="🎮 UNO Lobby",
            color=0xFFD700
        )

        embed.add_field(
            name="👥 Players",
            value="\n".join(
                p.mention
                for p in self.players
            ),
            inline=False
        )

        embed.set_footer(
            text=f"⏳ {self.seconds}s"
        )

        return embed

    @discord.ui.button(
        label="Join",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def join(
        self,
        interaction,
        button
    ):

        await interaction.response.defer()

        if interaction.user not in self.players:
            self.players.append(
                interaction.user
            )

        await self.message.edit(
            embed=self.make_embed(),
            view=self
        )

    @discord.ui.button(
        label="Leave",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def leave(
        self,
        interaction,
        button
    ):

        await interaction.response.defer()

        if interaction.user == self.host:
            return

        if interaction.user in self.players:
            self.players.remove(
                interaction.user
            )

        await self.message.edit(
            embed=self.make_embed(),
            view=self
        )


@bot.event
async def on_ready():

    await bot.tree.sync()

    print(f"READY: {bot.user}")

    print("Slash Commands Synced.")
@bot.command()
async def ping(ctx):

    await ctx.send(
        "🏓 Pong!"
    )


@bot.command(name="stop")
async def stop_game(ctx):

    if ctx.channel.id not in games:

        return await ctx.send(
            "❌ لا توجد مباراة."
        )

    game = games[
        ctx.channel.id
    ]

    try:

        game.finished = True

        if hasattr(game, "message") and game.message:

            await game.message.edit(
                content="🛑 تم إيقاف المباراة.",
                embed=None,
                attachments=[],
                view=None
            )

    except:
        pass

    del games[
        ctx.channel.id
    ]

    await ctx.send(
        "✅ تم إيقاف المباراة."
    )


@bot.command(name="إيقاف")
async def stop_game_ar(ctx):

    await stop_game(ctx)

@bot.command(name="uno")
async def uno_command(ctx):

    data = load_channels()

    allowed = data.get(str(ctx.guild.id))

    if allowed is not None:

        if ctx.channel.id != allowed:

            channel = bot.get_channel(allowed)

            if channel:
                return await ctx.send(
                    f"❌ يمكن لعب UNO فقط في {channel.mention}"
                )

            return await ctx.send(
                "❌ هذه ليست قناة UNO."
            )

    if ctx.channel.id in games:

        return await ctx.send(
            "❌ توجد مباراة بالفعل."
        )

    lobby = LobbyView(
        ctx.author
    )

    msg = await ctx.send(
        embed=lobby.make_embed(),
        view=lobby
    )

    lobby.message = msg

    games[
        ctx.channel.id
    ] = lobby

    for i in range(
        15,
        0,
        -1
    ):

        lobby.seconds = i

        try:
            await msg.edit(
                embed=lobby.make_embed(),
                view=lobby
            )
        except:
            pass

        await asyncio.sleep(1)

    game = UnoGame(
        lobby.players,
        ctx.author
    )

    games[
        ctx.channel.id
    ] = game

    try:
        await msg.delete()
    except:
        pass

    embed, file = create_game_embed(
        game
    )

    game_message = await ctx.send(
        embed=embed,
        file=file,
        view=GameView(
            game
        )
    )

    game.message = game_message
    
@bot.command(name="اونو")
async def arabic_uno(ctx):

    await uno_command(ctx)

# ---------- CHANNEL CONFIG ----------

CHANNEL_FILE = "channels.json"

if not os.path.exists(CHANNEL_FILE):
    with open(CHANNEL_FILE, "w") as f:
        json.dump({}, f)


def load_channels():
    with open(CHANNEL_FILE, "r") as f:
        return json.load(f)


def save_channels(data):
    with open(CHANNEL_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------- SLASH COMMANDS ----------

@bot.tree.command(
    name="unohelp",
    description="شرح طريقة لعب UNO"
)
async def unohelp(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎮 UNO Help",
        color=0x2ECC71
    )

    embed.add_field(
        name="🃏 الهدف",
        value="تخلص من جميع أوراقك قبل باقي اللاعبين.",
        inline=False
    )

    embed.add_field(
        name="🎨 البطاقات الخاصة",
        value=(
            "⏭️ Skip = تخطي اللاعب التالي\n"
            "🔄 Reverse = عكس الاتجاه\n"
            "➕2 Draw Two = يسحب اللاعب التالي ورقتين\n"
            "🌈 Wild = اختر أي لون\n"
            "➕4 Wild Draw Four = اختر لون + اللاعب التالي يسحب 4"
        ),
        inline=False
    )

    embed.add_field(
        name="‼️ UNO",
        value="إذا بقات عندك ورقة وحدة خاصك تضغط زر UNO قبل نهاية العداد.",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


@bot.tree.command(
    name="setchannel",
    description="تحديد قناة لعبة UNO"
)
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(
    interaction: discord.Interaction,
    channel: discord.TextChannel
):

    data = load_channels()

    data[str(interaction.guild.id)] = channel.id

    save_channels(data)

    await interaction.response.send_message(
        f"✅ تم تحديد {channel.mention} كقناة رسمية للعبة UNO.",
        ephemeral=True
    )

@setchannel.error
async def setchannel_error(interaction, error):

    if isinstance(error, app_commands.MissingPermissions):

        await interaction.response.send_message(
            "❌ يجب أن تكون Administrator.",
            ephemeral=True
        )


threading.Thread(
    target=run_web,
    daemon=True
).start()

ApplicationCommands(bot).register()

SendStage(bot).register()

AddQuestion(bot).register()

EditQuestion(bot).register()

ListQuestions(bot).register()

MessageListener(bot).register()

RemoveQuestion(bot).register()

bot.run(TOKEN)