# -*- coding: utf-8 -*-
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import Uuid, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    __table_args__ = {'extend_existing': True}


class MixinUid(Base):
    __abstract__ = True
    uid: Mapped[UUID] = mapped_column(Uuid, primary_key=True)


class MixinRemovable(Base):
    __abstract__ = True
    is_removed: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)


class MixinTimestamp(Base):
    __abstract__ = True
    date_created: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                   nullable=False)
    date_modified: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                    nullable=False,
                                                    onupdate=lambda: datetime.now(tz=timezone.utc))
