import asyncio
from sqlalchemy import text
from app.core.database import engine

async def list_tables():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
        for row in res:
            print(row[0])

if __name__ == "__main__":
    asyncio.run(list_tables())
