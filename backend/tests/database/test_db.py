import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.core.session import engine, async_session_maker, get_db  


@pytest.mark.asyncio
async def test_db_connection():
    async with async_session_maker() as session:

        result = await session.execute(select(1)) 
        assert result.scalar() == 1 
