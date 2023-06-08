import asyncio
from pathlib import Path
import signal

import click

from . import cxn, db, pipeline, context


async def run(**ctx_args):
    # TODO: Proper logging
    async with context.Context(**ctx_args) as ctx:
        # set up signal handlers for clean shutdown
        for sig in [signal.SIGINT]:
            asyncio.get_event_loop().add_signal_handler(sig, ctx.close)

        await ctx.start()

        # on __aexit__, Context waits for all the tasks to be completed, which
        # won't happen until `ctx.close` is called (i.e. by a signal handler)
        # so we very efficiently sit here doing nothing until then


@click.command(context_settings={'help_option_names': ['--help', '-h']})
@click.option(
    '-s', '--storage',
    help='Data storage location',
    type=click.Path(
        readable=True, writable=True, resolve_path=True,
        path_type=Path,
    ),
    required=True,
)
@click.option(
    '-d', '--discord-token',
    help='Discord API token for the bot account',
    prompt='Discord API token',
)
# TODO: Twitch
@click.option(
    '--clear-db/--keep-db',
    help='[DEBUG] Delete the DB before starting'
)
def main(clear_db: bool, **ctx_args):
    """
    Start a Catboy Maid software instance, which can host several Catboy Maids
    for several communities.
    """
    if clear_db:
        try:
            ctx_args['storage'].unlink()
        except FileNotFoundError:
            pass

    asyncio.run(run(**ctx_args))

