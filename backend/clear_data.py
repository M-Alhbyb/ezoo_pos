import asyncio
from sqlalchemy import text
from app.core.database import engine

async def clear_data():
    """
    Clears all data from the database by truncating tables.
    Uses CASCADE to handle foreign key dependencies.
    """
    tables = [
        "sale_items",
        "sale_payments",
        "sale_fees",
        "sales",
        "purchase_items",
        "purchases",
        "supplier_ledger",
        "suppliers",
        "inventory_log",
        "partner_wallet_transactions",
        "partner_distributions",
        "products",
        "categories",
        "partners",
        "payment_methods",
        "settings"
    ]
    
    async with engine.begin() as conn:
        print("--- Database Cleanup ---")
        for table in tables:
            try:
                # Check if table exists first to avoid noisy errors
                res = await conn.execute(text(f"SELECT to_regclass('public.{table}')"))
                if res.scalar():
                    await conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                    print(f"✅ Truncated: {table}")
                else:
                    print(f"ℹ️  Skipped: {table} (does not exist)")
            except Exception as e:
                print(f"❌ Error truncating {table}: {e}")
        
        # Reset payment methods with defaults
        print("\n--- Initializing Defaults ---")
        try:
            # First clear in case truncate failed or to be sure
            await conn.execute(text("DELETE FROM payment_methods"))
            
            await conn.execute(text("""
                INSERT INTO payment_methods (id, name, is_active, created_at, updated_at)
                VALUES 
                    (gen_random_uuid(), 'كاش', true, now(), now()),
                    (gen_random_uuid(), 'بنكك', true, now(), now())
            """))
            print("✅ Default payment methods (كاش، بنكك) added.")
        except Exception as e:
            print(f"ℹ️  Could not add default payment methods: {e}")

        print("\n✨ Database cleared and reset successfully!")

if __name__ == "__main__":
    asyncio.run(clear_data())
