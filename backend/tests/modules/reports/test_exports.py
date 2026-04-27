import pytest
from datetime import date
from app.modules.reports.export_service import ExportService

@pytest.mark.asyncio
async def test_generate_pdf_branded():
    # ExportService doesn't use db for the generation logic itself
    service = ExportService(None)
    data = [
        {"Item": "Solar Panel", "Quantity": 10, "Price": 500.0, "Notes": "High quality"},
        {"Item": "Inverter", "Quantity": 2, "Price": 1200.0, "Notes": "Standard"},
    ]
    meta_data = {"السيد": "Test Customer", "الموقع": "Dubai"}
    
    pdf_bytes = await service.generate_pdf(
        data=data,
        title="Test Branded Report",
        start_date=date.today(),
        end_date=date.today(),
        generated_by="test_user",
        meta_data=meta_data
    )
    
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0
    assert b"%PDF" in pdf_bytes

@pytest.mark.asyncio
async def test_generate_xlsx_branded():
    service = ExportService(None)
    data = [
        {"Item": "Solar Panel", "Quantity": 10, "Price": 500.0},
    ]
    meta_data = {"السيد": "Test Customer"}
    
    xlsx_buffer = await service.generate_xlsx(
        data=data,
        filename_prefix="test",
        start_date=date.today(),
        end_date=date.today(),
        title="Test Branded Excel",
        meta_data=meta_data
    )
    
    assert xlsx_buffer is not None
    assert xlsx_buffer.getbuffer().nbytes > 0
