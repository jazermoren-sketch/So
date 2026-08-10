import asyncio
from game.ai import play_ai


async def trigger_turn(game):
    if game.can_run_ai():
        asyncio.create_task(play_ai(game))