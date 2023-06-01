import asyncio
import contextlib
from dataclasses import dataclass
from pathlib import Path
import signal

import click
from sqlalchemy import create_engine, Engine

from . import cxn, db, pipeline


class Context:
    """
    Various bits and bobs that we pass around to everything to have one
    convenient reference.
    """

    def __init__(self, config, discord_token):
        self.es = contextlib.AsyncExitStack()
        self.tasks = asyncio.TaskGroup()

        engine = create_engine(f"sqlite:///{config}", echo=True)
        self.engine = engine

        self.discord = cxn.discord_client.DiscordClient(self, discord_token)
        # TODO: Twitch

    async def start(self):
        with self.engine.begin() as tx:
            db.base.SQLBase.metadata.create_all(tx, checkfirst=True)
        self.tasks.create_task(self.discord.spawn())
        # TODO: Twitch

    def close(self):
        self.tasks.create_task(self.discord.close())
        # TODO: Twitch

    async def __aenter__(self):
        self.tasks = await self.es.enter_async_context(self.tasks)
        return self

    async def __aexit__(self, *args):
        await self.es.__aexit__(*args)


async def run(**ctx_args):
    # TODO: Proper logging
    async with Context(**ctx_args) as ctx:
        # set up signal handlers for clean shutdown
        for sig in [signal.SIGINT]:
            asyncio.get_event_loop().add_signal_handler(sig, ctx.close)

        await ctx.start()

        # on __aexit__, Context waits for all the tasks to be completed, which
        # won't happen until `ctx.close` is called (i.e. by a signal handler)
        # so we very efficiently sit here doing nothing until then


@click.command(context_settings={'help_option_names': ['--help', '-h']})
@click.option(
    '-c', '--config',
    help='Data storage location',
    type=click.Path(
        readable=True, writable=True, resolve_path=True,
    ),
)
@click.option(
    '-d', '--discord-token',
    help='Discord API token for the bot account',
    prompt='Discord API token',
)
def main(**ctx_args):
    """
    Start a Catboy Maid software instance, which can host several Catboy Maids
    for several communities.
    """
    asyncio.run(run(**ctx_args))

