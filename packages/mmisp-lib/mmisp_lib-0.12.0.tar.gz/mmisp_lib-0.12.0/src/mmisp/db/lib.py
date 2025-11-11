import logging

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

logger = logging.getLogger("mmisp")


async def get_count_from_select(db: AsyncSession, query: Select) -> int:
    logger.debug("Get count from query: %s", query)
    count_query = (
        query.with_only_columns(func.count(), maintain_column_froms=True).order_by(None).limit(None).offset(None)
    )
    logger.debug("Resulted count query: %s", count_query)
    result = await db.execute(count_query)
    return result.scalar()
