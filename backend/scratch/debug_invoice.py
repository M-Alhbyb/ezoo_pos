
import asyncio
import os
import sys
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))

from app.modules.pos.service import SaleService
from app.modules.reports.export_service import ExportService
from app.core.database import AsyncSessionLocal

async def test_invoice_gen():
    async with AsyncSessionLocal() as db:
        service = SaleService(db)
        export_service = ExportService(db)
        
        # Get a real sale ID
        from sqlalchemy import select
        from app.models.sale import Sale
        result = await db.execute(select(Sale).limit(1))
        initial_sale = result.scalar_one_or_none()
        
        if not initial_sale:
            print("No sales found")
            return

        sale = await service.get_sale_detail(initial_sale.id)
        if not sale:
            print(f"Failed to fetch details for sale {initial_sale.id}")
            return

        print(f"Testing invoice generation for sale {sale.id}")
        
        # This is what pos/routes.py does
        from app.modules.pos.routes import _prepare_sale_response
        sale_data = await _prepare_sale_response(sale)
        
        if sale.customer:
            sale_data["customer_name"] = sale.customer.name
        else:
            sale_data["customer_name"] = "Walk-in Customer"

        try:
            pdf_content = await export_service.generate_sale_invoice_pdf(sale_data)
            print(f"PDF generated successfully, size: {len(pdf_content)} bytes")
            with open("debug_invoice.pdf", "wb") as f:
                f.write(pdf_content)
        except Exception as e:
            print(f"FAILED with error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_invoice_gen())
