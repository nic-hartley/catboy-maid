"""
The database-wide base type.
"""

from datetime import datetime, timedelta
import random
import re
from typing import Literal

from sqlalchemy import *
from sqlalchemy.event import *
from sqlalchemy.orm import *

from ..deco import with_session
from ..context import Context


class SQLBase(DeclarativeBase):
    """
    Something stored in the database. Comes with some common, broadly shared
    framework.
    """

    @declared_attr.directive
    def __tablename__(cls):
        return cls.__name__

    # Unique ID for this row
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    @with_session
    def log(self, ctx: Context, sesh: Session, message: str, **life):
        sesh.add(AuditLog(
            item_type=self.__tablename__,
            item_id=self.id,
            lifetime=timedelta(**life),
            message=message,
        ))


class AuditLog(SQLBase):
    """
    Logs taken every time something important happens, in the caller's eyes
    """

    item_type: Mapped[str]
    item_id: Mapped[int]
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
    lifetime: Mapped[timedelta]
    message: Mapped[str]


next_clean = datetime.now()
@listens_for(Session, 'before_commit')
def clean_old_audit_logs(sesh: Session):
    global next_clean
    if next_clean > datetime.now():
        return
    sesh.execute(
        delete(AuditLog)
        .where(AuditLog.timestamp + AuditLog.lifetime < func.now())
    )
    next_clean = datetime.now() + timedelta(minutes=5)
