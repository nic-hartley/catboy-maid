import asyncio
from dataclasses import dataclass
from pathlib import Path
import signal

import click
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from . import cxn, db, pipeline


class Context:
    """
    Various bits and bobs that we pass around to everything to have one
    convenient reference.
    """
    # discord: cxn.discord.DiscordClient
    # twitch: cxn.twitch.TwitchClient
    group: asyncio.TaskGroup
    engine: AsyncEngine

    def close(self):
        # TODO: if self.discord: self.discord.close()
        # TODO: if self.twitch: self.twitch.close()
        pass


async def run(config, discord_token, twitch_token):
    engine = create_async_engine(f"sqlite://{config}", echo=True)
    async with engine.begin() as tx:
        await tx.run_sync(db.base.SQLBase.metadata.create_all)
    async with asyncio.TaskGroup() as tg:
        ctx = Context(None, None, tg, engine)
        asyncio.get_event_loop().add_signal_handler(signal.SIGINT, ctx.close)

        # TODO: ctx.discord = cxn.discord.DiscordClient(ctx)
        # TODO: ctx.twitch = cxn.twitch.TwitchClient(ctx)

        # task group __exit__ will automatically wait until things are done,
        # most notably the runner tasks that the clients add to the TaskGroup
        # (i.e. until Ctrl+C calls ctx.close)
    # TODO: await ctx.discord.close()
    # TODO: await ctx.twitch.close()


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
@click.option(
    '-t', '--twitch-token',
    help='Twitch API token for the bot account',
    prompt='Twitch API token',
)
def main(config, discord_token, twitch_token):
    """
    Start a Catboy Maid software instance, which can host several Catboy Maids
    for several communities.
    """
    asyncio.run(run(config, discord_token, twitch_token))

