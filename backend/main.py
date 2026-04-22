from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.database import get_db
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.websocket.manager import manager
from app.modules.products.routes import router as products_router
from app.modules.categories.routes import router as categories_router
from app.modules.pos.routes import router as pos_router
from app.modules.inventory.routes import router as inventory_router
from app.modules.settings.routes import router as settings_router
from app.modules.partners.routes import router as partners_router
from app.modules.reports.routes import router as reports_router
from app.modules.suppliers.routes import router as suppliers_router
from app.modules.purchases.routes import router as purchases_router
from app.modules.customers.routes import router as customers_router
from app.api.routes.dashboard import router as dashboard_router
import logging

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        f"{settings.app_description}\n\n"
        "## Export Endpoints (003-export-visualization-dashboards)\n\n"
        "- `GET /api/reports/sales/export` - Export sales report (CSV, XLSX, PDF)\n"
        "- `GET /api/reports/partners/export` - Export partners report (CSV, XLSX, PDF)\n"
        "- `GET /api/reports/inventory/export` - Export inventory report (CSV, XLSX, PDF)\n\n"
        "## Dashboard Endpoints (003-export-visualization-dashboards)\n\n"
        "- `GET /api/dashboard/sales` - Sales line chart data with date range filter\n"
        "- `GET /api/dashboard/partners` - Partner dividends pie chart data\n"
        "- `GET /api/dashboard/inventory` - Inventory stacked bar chart data\n\n"
        "## Limits\n\n"
        f"- CSV max rows: {settings.csv_max_rows:,}\n"
        f"- XLSX max rows: {settings.xlsx_max_rows:,}\n"
        f"- PDF max rows: {settings.pdf_max_rows:,}\n"
        f"- Dashboard max points: {settings.dashboard_max_points:,}\n"
        f"- Rate limit threshold: {settings.export_rate_limit_threshold:,} rows\n"
    ),
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(categories_router)
app.include_router(pos_router)
app.include_router(inventory_router)
app.include_router(settings_router)
app.include_router(partners_router)
app.include_router(reports_router)
app.include_router(suppliers_router)
app.include_router(purchases_router)
app.include_router(customers_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    return {"message": "EZOO POS API", "version": settings.app_version}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/payment-methods")
async def get_payment_methods(db: AsyncSession = Depends(get_db)):
    """Get all active payment methods (compatibility endpoint)."""
    from sqlalchemy import select
    from app.models.payment_method import PaymentMethod

    result = await db.execute(
        select(PaymentMethod).where(PaymentMethod.is_active == True)
    )
    methods = result.scalars().all()
    return {"items": [m.to_dict() for m in methods]}


@app.websocket("/ws/stock-updates")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time stock updates.

    POS clients connect to this endpoint to receive real-time notifications
    when stock levels change due to sales, reversals, restocks, or adjustments.

    The connection automatically reconnects on disconnect and displays
    connection status to the operator.

    Message format (stock update):
        {
            "event": "stock_updated",
            "data": {
                "product_id": "uuid",
                "stock_quantity": 48
            }
        }

    Message format (batch update):
        {
            "event": "stock_updated_batch",
            "data": [
                {"product_id": "uuid1", "stock_quantity": 48},
                {"product_id": "uuid2", "stock_quantity": 12}
            ]
        }
    """
    await manager.connect(websocket)
    try:
        # Keep connection alive and listen for any client messages
        # (primarily used for heartbeat/ping-pong to detect disconnections)
        while True:
            # Wait for any message from client (ping/pong)
            # If client disconnects, this will raise WebSocketDisconnect
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
