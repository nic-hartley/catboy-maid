"""
Discord-specific entrypoints to the pipelines
"""

from datetime import datetime

from discord import ChannelType, Guild, TextChannel, Object, Message
from discord.abc import GuildChannel
from sqlalchemy import *
from sqlalchemy.orm import *

from ..deco import export, with_session
from ..context import Context
from .. import db


@with_session
async def get_guild(ctx: Context, sesh: Session, api: Guild, *, create = True):
    in_db = sesh.scalar(
        select(db.discord.DiscordServer)
        .where(db.discord.DiscordServer.discord_id == api.id)
    )
    if in_db is not None:
        return in_db
    elif not create:
        assert False, "expected guild but not found"
    else:
        new = db.discord.DiscordServer(
            discord_id=api.id,
            c2_channel=None,
        )
        sesh.add(new)
        return new


@export
@with_session
async def update_all_guilds(ctx: Context, sesh: Session, guilds: list[Guild]):
    for guild in guilds:
        await update_guild(ctx, guild)


@export
@with_session
async def update_guild(ctx: Context, sesh: Session, guild: Guild):
    db_guild = await get_guild(ctx, guild)

    for chan in guild.channels:  # type: TextChannel
        if not chan.type == ChannelType.text:
            continue
        latest: db.discord.DiscordMessage = sesh.scalar(
            select(db.discord.DiscordMessage)
            .where(db.discord.DiscordMessage.channel == chan.id)
            .order_by(db.discord.DiscordMessage.posted_at.desc())
            .limit(1)
        )
        if latest:
            if latest.discord_id == chan.last_message_id:
                continue
            since = Object(latest.discord_id)
        else:
            since = None
        async for msg in chan.history(after=since):
            await add_message(ctx, msg, db_guild=db_guild)


@export
@with_session
async def add_message(
    ctx: Context, sesh: Session, msg: Message,
    *, db_guild: Guild | None = None,
):
    if ctx.discord.user.id == msg.author.id:
        return
    if db_guild is None:
        db_guild = await get_guild(ctx, msg.channel.guild, create=False)
    sesh.add(db.discord.DiscordMessage(
        discord_id=msg.id,
        text=msg.content,
        server=db_guild,
        server_id=db_guild.id,
        channel=msg.channel.id,
        posted_at=msg.created_at,
    ))


@export
@with_session
async def delete_message(
    ctx: Context, sesh: Session, msg_id: int,
):
    in_db: db.discord.DiscordMessage = sesh.scalar(
        select(db.discord.DiscordMessage)
        .where(db.discord.DiscordMessage.discord_id == msg_id)
    )
    if in_db is not None:
        in_db.deleted_at = datetime.now()
