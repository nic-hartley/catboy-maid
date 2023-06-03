"""
Discord-specific entrypoints to the pipelines
"""

from datetime import datetime

from discord import ChannelType, Guild, TextChannel, Object, Message
from discord.abc import GuildChannel
from sqlalchemy import *
from sqlalchemy.orm import *

from ..context import Context
from ..db import discord_db
from . import with_session

@with_session
async def update_guild(ctx: Context, sesh: Session, guild: Guild):
    db_guild = discord_db.DiscordServer(
        discord_id=guild.id,
        c2_channel=None,
    )
    sesh.add(db_guild)

    for chan in guild.channels:  # type: TextChannel
        if not chan.type == ChannelType.text:
            continue
        latest: discord_db.DiscordMessage = sesh.scalar(
            select(discord_db.DiscordMessage)
            .where(discord_db.DiscordMessage.channel == chan.id)
            .order_by(discord_db.DiscordMessage.posted_at.desc())
            .limit(1)
        )
        if latest:
            since = Object(latest.discord_id)
        else:
            since = None
        if since == chan.last_message_id:
            continue
        async for msg in chan.history(after=since):
            await add_message(ctx, msg, db_guild=db_guild)


@with_session
async def add_message(
    ctx: Context, sesh: Session, msg: Message,
    *, db_guild: Guild | None = None,
):
    if db_guild is None:
        db_guild = sesh.scalar(
            select(discord_db.DiscordServer)
            .where(discord_db.DiscordServer.discord_id == msg.guild.id)
        )
    if db_guild is None:  # still??
        raise ValueError("attempted to create message without the server")
    sesh.add(discord_db.DiscordMessage(
        discord_id=msg.id,
        text=msg.content,
        server=db_guild,
        server_id=db_guild.id,
        channel=msg.channel.id,
        posted_at=msg.created_at,
    ))


@with_session
async def delete_message(
    ctx: Context, sesh: Session, msg_id: int,
):
    in_db: discord_db.DiscordMessage = sesh.scalar(
        select(discord_db.DiscordMessage)
        .where(discord_db.DiscordMessage.discord_id == msg_id)
    )
    if in_db is not None:
        in_db.deleted_at = datetime.now()
