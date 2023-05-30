"""
The database-wide base type.
"""

import random
import re

from sqlalchemy import *
from sqlalchemy.orm import *


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
