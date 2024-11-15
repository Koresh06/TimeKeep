import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.core.session import async_session_maker


@pytest.mark.asyncio
async def test_db_connection():
    async with async_session_maker() as session:

        result = await session.execute(select(1)) 
        assert result.scalar() == 1 
