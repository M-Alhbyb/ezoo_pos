import asyncio
import sys
import os
from decimal import Decimal
from sqlalchemy import select
from app.core.database import engine, AsyncSessionLocal
from app.models.category import Category
from app.models.product import Product

async def seed_data():
    data = {
        "Electronics": [
            ("Inverter 1000W Pure Sine", "INV-1000-PS", 450, 750, 10),
            ("Inverter 2000W Pure Sine", "INV-2000-PS", 800, 1300, 5),
            ("Charge Controller 60A MPPT", "CC-60-MPPT", 180, 320, 25),
            ("Charge Controller 40A MPPT", "CC-40-MPPT", 120, 210, 15),
            ("DC Circuit Breaker 63A", "CB-63A-DC", 15, 45, 40),
        ],
        "Solar Energy": [
            ("550W Mono Solar Panel", "PAN-550-MONO", 850, 1400, 60),
            ("450W Mono Solar Panel", "PAN-450-MONO", 700, 1100, 40),
            ("200A LiFePO4 Battery", "BAT-200-LIFE", 1200, 1950, 12),
            ("100A Gel Battery", "BAT-100-GEL", 400, 700, 30),
            ("150A Gel Battery", "BAT-150-GEL", 550, 950, 20),
        ],
        "Mounting Equipment": [
            ("Aluminum L-Feet", "MNT-L-FEET", 5, 12, 200),
            ("Rail Splice Kit", "MNT-SPLICE", 3, 8, 100),
            ("End Clamp 35mm", "MNT-END-35", 2, 6, 300),
            ("Mid Clamp 35mm", "MNT-MID-35", 2, 6, 500),
            ("Roof Rail 4.2m", "MNT-RAIL-4.2", 40, 85, 50),
        ],
        "Accessories": [
            ("MC4 Connector Pair", "ACC-MC4-PAIR", 1.5, 5, 500),
            ("Solar Cable 4mm Black (m)", "ACC-CABL-4BK", 0.8, 2.5, 1000),
            ("Solar Cable 4mm Red (m)", "ACC-CABL-4RD", 0.8, 2.5, 1000),
        ],
        "Tools": [
            ("MC4 Crimping Tool", "TL-MC4-CRIMP", 25, 65, 10),
            ("Multimeter Digital", "TL-MULTI-DIGI", 15, 45, 15),
        ]
    }

    async with AsyncSessionLocal() as session:
        print("Seeding test data...")
        
        for cat_name, products in data.items():
            # Create or get category
            cat = (await session.execute(select(Category).where(Category.name == cat_name))).scalar_one_or_none()
            if not cat:
                cat = Category(name=cat_name)
                session.add(cat)
                await session.flush()
                print(f"Created category: {cat_name}")
            
            for name, sku, base, selling, stock in products:
                # Check if product exists
                prod = (await session.execute(select(Product).where(Product.sku == sku))).scalar_one_or_none()
                if not prod:
                    prod = Product(
                        name=name,
                        sku=sku,
                        category_id=cat.id,
                        base_price=Decimal(str(base)),
                        selling_price=Decimal(str(selling)),
                        stock_quantity=stock,
                        is_active=True
                    )
                    session.add(prod)
                    print(f"  Added product: {name}")
        
        await session.commit()
        print("\nSeeding complete!")
        
        # Verify counts
        cat_count = (await session.execute(select(Category))).all()
        prod_count = (await session.execute(select(Product))).all()
        print(f"Total categories: {len(cat_count)}")
        print(f"Total products: {len(prod_count)}")

if __name__ == "__main__":
    asyncio.run(seed_data())
