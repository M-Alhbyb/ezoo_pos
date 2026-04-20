import asyncio
import random
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.product import Product
from app.models.payment_method import PaymentMethod
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.inventory_log import InventoryLog
from app.modules.pos.service import SaleService
from app.schemas.sale import SaleCreate, SaleItemCreate

async def seed_fake_sales():
    async with AsyncSessionLocal() as session:
        print("Fetching products and payment methods...")
        
        # Get active payment method IDs
        pm_res = await session.execute(select(PaymentMethod).where(PaymentMethod.is_active == True))
        pm_ids = [str(pm.id) for pm in pm_res.scalars().all()]
        
        if not pm_ids:
            print("No active payment methods found. Please create one first.")
            return

        sale_service = SaleService(session)
        num_sales = 20
        print(f"Generating {num_sales} fake sales...")

        for i in range(num_sales):
            # Fetch products fresh each time to avoid expiration issues and get current stock
            products_res = await session.execute(select(Product).where(Product.is_active == True))
            products = products_res.scalars().all()
            
            # Map products to plain dicts to avoid lazy loading issues
            product_data = [
                {"id": p.id, "name": p.name, "stock": p.stock_quantity}
                for p in products if p.stock_quantity > 0
            ]
            
            if not product_data:
                print("No products with stock found.")
                break

            # Pick 1-3 random products
            selected_indices = random.sample(range(len(product_data)), k=random.randint(1, min(3, len(product_data))))
            
            items = []
            for idx in selected_indices:
                p = product_data[idx]
                qty = random.randint(1, min(3, p["stock"]))
                items.append(SaleItemCreate(product_id=p["id"], quantity=qty))
            
            if not items:
                continue

            # Pick random payment method ID
            pm_id = random.choice(pm_ids)
            
            # Random date within last 30 days
            days_ago = random.randint(0, 30)
            target_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))

            sale_create = SaleCreate(
                items=items,
                payment_method_id=pm_id,
                fees=[],
                note=f"Fake transaction {i+1}",
                idempotency_key=f"fake_sale_{i+1}_{target_date.timestamp()}"
            )

            try:
                # Create the sale using service
                sale = await sale_service.create_sale(sale_create)
                
                # Update timestamps
                await session.execute(
                    update(Sale)
                    .where(Sale.id == sale.id)
                    .values(created_at=target_date)
                )
                await session.execute(
                    update(SaleItem)
                    .where(SaleItem.sale_id == sale.id)
                    .values(created_at=target_date)
                )
                await session.execute(
                  update(InventoryLog)
                  .where(InventoryLog.reference_id == sale.id)
                  .values(created_at=target_date)
                )
                
                await session.commit()
                print(f"  Created sale {i+1}/{num_sales} dated {target_date.date()}")
                
            except Exception as e:
                print(f"  Error creating sale {i+1}: {e}")
                await session.rollback()

        print("\nFake sales seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_fake_sales())
