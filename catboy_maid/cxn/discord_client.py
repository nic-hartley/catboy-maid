import functools
import inspect
import random

import discord
from sqlalchemy.orm import Session

from ..db import discord_db


COMMANDS = []
def pycord_sanifier(fn: discord.ApplicationCommand):
    """
    Untangles a bit of pycord insanity.
    """
    orig_callback = fn.callback
    @functools.wraps(orig_callback)
    async def deco(ctx, **kwargs):
        return await orig_callback(ctx.bot, ctx, **kwargs)
    sig = inspect.signature(orig_callback)
    deco.__signature__ = sig.replace(parameters=[
        param
        for param in sig.parameters.values()
        if param.name != 'self'
    ])
    fn.callback = deco
    COMMANDS.append(fn)
    return fn


class DiscordClient(discord.Bot):
    def __init__(self, ctx, token):
        super().__init__(intents=discord.Intents(
            guilds=True,
        ))
        self.__ctx = ctx
        self.__token = token
        for command in COMMANDS:
            self.add_application_command(command)

    async def spawn(self):
        await self.login(self.__token)
        await self.sync_commands(force=True)
        await self.connect()

    @pycord_sanifier
    @discord.commands.slash_command()
    async def ping(self, ctx: discord.ApplicationContext, extra: bool = False):
        """
        Check whether your Catboy Maid is responding.
        """
        message = random.choice([
            "pong <3",
            "miao",
            "mya~!",
            "mrrrrrr...",
            "awoooooooo",
            "aaah! im awake im awake!!!",
            "yea yea you don't gotta be so loud about it",
            "sfdddff ih hi. hi. im here. mrow."
        ])
        if extra:
            text = f"""
            {message}

            my latency is: {self.latency:.02f}s.
            """
        else:
            text = message
        await ctx.respond(inspect.cleandoc(text), ephemeral=True)

    async def on_ready(self):
        with Session(self.__ctx.engine) as sesh:
            sesh.add_all(
                discord_db.DiscordServer(
                    discord_id=guild.id,
                    c2_channel=None,
                )
                for guild in self.guilds
            )
            sesh.commit()

    async def on_guild_join(self, guild: discord.Guild):
        with self.__ctx.engine.begin() as sesh:
            sesh.add(discord_db.DiscordServer(
                discord_id=guild.id,
                c2_channel=None,
            ))
            sesh.commit()
        self.__ctx.tasks.create_task(coro)
