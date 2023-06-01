import functools
import inspect
import random

import discord


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
        super().__init__()
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
    async def ping(self, ctx: discord.ApplicationContext):
        """
        Check whether your Catboy Maid is responding.
        """
        await ctx.respond(random.choice([
            "pong <3",
            "miao",
            "mya~!",
            "awoooooooo",
            "aaah! im awake im awake!!!",
            "yea yea you don't gotta be so loud about it",
        ]))

    # TODO: Handle events
