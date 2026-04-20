
import asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load from backend/.env
load_dotenv("backend/.env")

DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")

async def check_sales():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        from app.models.sale import Sale
        count_stmt = select(func.count(Sale.id))
        result = await session.execute(count_stmt)
        count = result.scalar()
        print(f"Total sales in database: {count}")
        
        latest_sale_stmt = select(Sale).order_by(Sale.created_at.desc()).limit(1)
        result = await session.execute(latest_sale_stmt)
        latest_sale = result.scalar()
        if latest_sale:
            print(f"Latest sale: {latest_sale.id} at {latest_sale.created_at}")
            
            # Check sales in the last 30 days
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_stmt = select(func.count(Sale.id)).where(Sale.created_at >= thirty_days_ago)
            result = await session.execute(recent_stmt)
            recent_count = result.scalar()
            print(f"Sales in last 30 days: {recent_count}")
        else:
            print("No sales found.")

if __name__ == "__main__":
    asyncio.run(check_sales())
