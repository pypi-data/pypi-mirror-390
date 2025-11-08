# -*- coding: utf-8 -*-
from sqlalchemy.sql import Select, Delete
from sqlalchemy.ext.asyncio import AsyncSession


async def fetch_first(sess: AsyncSession, expression: Select, for_update: bool = False):
    return (await sess.scalar(
        expression.with_for_update() if for_update else expression
    ))


async def fetch_all(sess: AsyncSession, expression: Select, for_update: bool = False):
    return (await sess.scalars(
        expression.with_for_update() if for_update else expression
    )).all()


async def execute(sess: AsyncSession, expression: Select | Delete):
    """
    Execute a SQL expression in the SQLAlchemy async session.
    :param sess: SQLAlchemy database async session.
    :param expression: The SQL expression to execute.
    :return: SQLAlchemy expression execution result.
    """
    return await sess.execute(expression)


async def scalar(sess: AsyncSession, expression: Select):
    return (await execute(sess, expression)).scalar()


async def fetch_iterate(sess: AsyncSession, expression: Select, for_update: bool = False):
    return await sess.stream_scalars(
        expression.with_for_update() if for_update else expression
    )
