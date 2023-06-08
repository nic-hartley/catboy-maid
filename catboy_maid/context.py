import asyncio
import contextlib
from pathlib import Path
import typing as t

from sqlalchemy import create_engine, Engine

class Context:
    """
    Various bits and bobs that we pass around to everything to have one
    convenient reference.
    """

    def __init__(self, storage: Path, discord_token: str):
        # import is here to break the import loop
        from . import cxn, db

        self.es = contextlib.AsyncExitStack()
        self.tasks = asyncio.TaskGroup()

        engine = create_engine(f"sqlite:///{storage}", echo=True)
        self.engine = engine

        self.discord = cxn.discord.DiscordClient(self, discord_token)
        # TODO: Twitch

    async def start(self):
        # import is here to break the import loop
        from . import db

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

    def run(self, fn: t.Callable[[t.Any, ...], t.Awaitable[t.Any]], *args, **kwargs):
        self.tasks.create_task(fn(self, *args, **kwargs))
