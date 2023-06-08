import functools
import inspect
import random

import discord

from .. import pipeline

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
            messages=True,
            message_content=True,
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
        self.__ctx.run(pipeline.discord.update_all_guilds, self.guilds)

    async def on_guild_join(self, guild: discord.Guild):
        self.__ctx.run(pipeline.discord.update_guild, guild)

    async def on_message(self, message: discord.Message):
        self.__ctx.run(pipeline.discord.add_message, message)

    async def on_raw_message_delete(self, ev: discord.RawMessageDeleteEvent):
        self.__ctx.run(pipeline.discord.delete_message, ev.message_id)
