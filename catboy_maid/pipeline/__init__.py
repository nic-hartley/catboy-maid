"""
Each submodule here is a closely related set of actions and processing, all
triggered by database events and only (directly) affecting the database.
"""


from contextvars import Context, ContextVar
import functools
import inspect

from sqlalchemy.orm import Session


SESSION = ContextVar('SESSION')
def with_session(fn):
    @functools.wraps(fn)
    async def deco(ctx, *args, **kwargs):
        if sesh := SESSION.get(None):
            return await fn(ctx, sesh, *args, **kwargs)


        with Session(ctx.engine) as sesh:
            sesh.begin()
            SESSION.set(sesh)
            res = await fn(ctx, sesh, *args, **kwargs)
            sesh.commit()
        return res
    sig = inspect.signature(deco)
    deco.__signature__ = sig.replace(parameters=[
        param
        for param in sig.parameters.values()
        if param.name != 'sesh'
    ])
    return deco


from . import discord_pipe
