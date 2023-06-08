"""
Miscellaneous useful decorators.
"""

from contextvars import Context, ContextVar
import functools
import inspect
import sys

from sqlalchemy.orm import Session

__all__ = ['export']


def export(fn):
    module = sys.modules[fn.__module__]
    if not hasattr(module, '__all__'):
        module.__all__ = []
    module.__all__.append(fn.__name__)
    return fn


SESSION = ContextVar('SESSION')
@export
def with_session(fn):
    sig = inspect.signature(fn)
    has_self = 'self' in sig.parameters
    params = list(sig.parameters.keys())
    assert params[0 + has_self] == 'ctx'
    assert params[1 + has_self] == 'sesh'

    @functools.wraps(fn)
    async def deco(*args, **kwargs):
        if has_self:
            pre = [args.pop(0)]
        else:
            pre = []
        ctx, *rest = args

        if sesh := SESSION.get(None):
            return await fn(*pre, ctx, sesh, *rest, **kwargs)

        with Session(ctx.engine) as sesh:
            sesh.begin()
            SESSION.set(sesh)
            res = await fn(*pre, ctx, sesh, *rest, **kwargs)
            sesh.commit()
        return res
    deco.__signature__ = sig.replace(parameters=[
        param
        for param in sig.parameters.values()
        if param.name != 'sesh'
    ])
    return deco
