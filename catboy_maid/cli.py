import asyncio
from pathlib import Path

import click
from sqlalchemy import create_async_engine

from . import cxn, db, pipeline

@click.command()
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
    engine = create_async_engine(f"sqlite://{config}", echo=True)
    with asyncio.Runner() as runner:
        pass  # TODO: Run stuff
