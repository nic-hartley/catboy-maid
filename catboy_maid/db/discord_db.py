"""
Discord-specific types.

These are also generally your gateway into actually interacting with the
platforms.
"""

from __future__ import annotations
from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import *

from .base import SQLBase

class Discord:
    """
    Something with a Discord ID (sometimes called a snowflake)
    """
    discord_id: Mapped[int | None] = mapped_column(unique=True)


class DiscordMessage(Discord, SQLBase):
    """
    A single message on a Discord server.
    """
    # author: Mapped[User]
    text: Mapped[str]
    server: Mapped[DiscordServer] = relationship(back_populates="messages")
    server_id: Mapped[int] = mapped_column(ForeignKey("DiscordServer.id"))
    channel: Mapped[int]
    posted_at: Mapped[datetime]
    deleted_at: Mapped[datetime | None]


class DiscordServer(Discord, SQLBase):
    """
    A single Discord server, which belongs to a community.

    Each Discord server can have a channel designated as Catboy Maid's C2
    channel, where it posts notifications relevant to the whole community.
    Every community has to have at least one C2 channel across all its
    Discord servers.
    """
    # community: Mapped[Community] = relationship(back_populates="discords")
    c2_channel: Mapped[int | None]
    messages: Mapped[list[DiscordMessage]] = relationship(back_populates="server")
