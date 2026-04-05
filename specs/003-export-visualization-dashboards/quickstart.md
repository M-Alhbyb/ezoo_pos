# Quickstart: Export Formats and Visualization Dashboards

**Feature**: 003-export-visualization-dashboards  
**Date**: 2026-04-05  
**Estimated Time**: 2-3 sprints (6-9 days)

## Prerequisites

- Python 3.11 environment
- PostgreSQL database with EZOO POS Phase 4 data
- Node.js 18+ for frontend development
- Existing EZOO POS codebase (backend + frontend)

## Quick Setup

### 1. Install Backend Dependencies

```bash
cd backend

# Add torequirements.txt
pandas==2.1.4
ReportLab==4.0.7
slowapi==0.1.9

# Install
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend

# Add to package.json
npm install recharts@2.10.3

# Install
npm install
```

### 3. Environment Variables

Add to `backend/.env`:

```bash
# Export limits
CSV_MAX_ROWS=100000
XLSX_MAX_ROWS=50000
PDF_MAX_ROWS=10000

# Rate limiting
EXPORT_RATE_LIMIT_THRESHOLD=5000
EXPORT_RATE_LIMIT_PER_HOUR=10

# Dashboard limits
DASHBOARD_MAX_POINTS=1000

# Timeouts
EXPORT_TIMEOUT_SECONDS=30
DASHBOARD_TIMEOUT_SECONDS=3
```

## Development Workflow

### Backend: Sprint 1 (Days 1-3)

#### Day 1: Export Service Foundation

```bash
# Create export service
touch src/app/modules/reports/export_service.py
touch src/app/schemas/export.py
touch tests/unit/test_export_service.py
```

**Implement**:
1. `ExportService` class with format-specific generation methods
2. `ExportRequest` and `ExportMetadata` Pydantic schemas
3. Row count validation before generation
4. Decimal precision preservation in pandas

**Test**:
```bash
pytest tests/unit/test_export_service.py -v
```

#### Day 2: Export API Endpoints

```bash
# Extend existing routes
# Edit: src/app/api/routes/reports.py
```

**Implement**:
1. `GET /api/reports/sales/export` endpoint
2. `GET /api/reports/projects/export` endpoint
3. `GET /api/reports/partners/export` endpoint
4. `GET /api/reports/inventory/export` endpoint

**Test**:
```bash
pytest tests/integration/test_export_endpoints.py -v
```

#### Day 3: Rate Limiting & Progress

**Implement**:
1. Slowapi rate limiting for large exports
2. WebSocket progress messages
3. Cancellation endpoint
4. Integration tests

### Backend: Sprint 2 (Days 4-6)

#### Day 4: Dashboard Service Foundation

```bash
# Create dashboard service
touch src/app/modules/reports/dashboard_service.py
touch src/app/schemas/dashboard.py
touch tests/unit/test_dashboard_service.py
```

**Implement**:
1. `DashboardService` class with aggregation methods
2. `DashboardFilter` and `ChartData` Pydantic schemas
3. SQLAlchemy GROUP BY queries for chart data
4. Data point limit validation (1000 max)

**Test**:
```bash
pytest tests/unit/test_dashboard_service.py -v
```

#### Day 5: Dashboard API Endpoints

```bash
# Create new routes
touch src/app/api/routes/dashboard.py
touch tests/integration/test_dashboard_endpoints.py
```

**Implement**:
1. `GET /api/dashboard/sales` endpoint
2. `GET /api/dashboard/projects` endpoint
3. `GET /api/dashboard/partners` endpoint
4. `GET /api/dashboard/inventory` endpoint

**Test**:
```bash
pytest tests/integration/test_dashboard_endpoints.py -v
```

#### Day 6: Integration & Logging

**Implement**:
1. Error logging for exports and dashboards (FR-042, FR-043)
2. Integration tests for full workflows
3. Performance testing for 10k row exports
4. WebSocket integration tests

**Test**:
```bash
pytest tests/ -k "export or dashboard" -v
```

### Frontend: Sprint 3 (Days 7-9)

#### Day 7: Chart Components

```bash
# Create chart components
mkdir -p src/components/charts
touch src/components/charts/LineChart.tsx
touch src/components/charts/BarChart.tsx
touch src/components/charts/PieChart.tsx
touch src/components/charts/StackedBarChart.tsx
```

**Implement**:
1. Reusable Recharts components
2. Custom tooltip with Decimal precision
3. Responsive containers
4. Empty state handling

**Test**:
```bash
npm test -- components/charts
```

#### Day 8: Dashboard Pages

```bash
# Create dashboard pages
mkdir -p src/app/dashboard/sales
mkdir -p src/app/dashboard/projects
mkdir -p src/app/dashboard/partners
mkdir -p src/app/dashboard/inventory
```

**Implement**:
1. Sales dashboard page with line chart
2. Projects dashboard page with bar chart
3. Partners dashboard page with pie chart
4. Inventory dashboard page with stacked bar chart

**Test**:
```bash
npm test -- app/dashboard
```

#### Day 9: Export Integration & Polish

**Implement**:
1. Export buttons on existing report pages
2. Progress indicator with cancellation
3. File download handling
4. Error display for limit violations

**Test**:
```bash
npm run build
npm run test
```

## Testing Quickstart

### Backend Unit Tests

```python
# tests/unit/test_export_service.py

import pytest
from decimal import Decimal
from app.modules.reports.export_service import ExportService
from app.schemas.export import ExportFormat

@pytest.mark.asyncio
async def test_export_csv_preserves_decimals(export_service, sample_sales_data):
    """Test that CSV export preserves Decimal precision"""
    result = await export_service.generate_csv(sample_sales_data)
    
    # Parse CSV and verify precision
    lines = result.decode('utf-8').split('\n')
    assert '1250.5000' in lines[1]  # Decimal preserved to 4 places

@pytest.mark.asyncio
async def test_export_rejects_exceeds_row_limit(export_service):
    """Test that row limit is enforced before generation"""
    with pytest.raises(RowLimitExceededError) as exc:
        await export_service.generate_csv(
            format=ExportFormat.CSV,
            start_date=date(2020, 1, 1),
            end_date=date(2026, 12, 31)  # Exceeds100k rows
        )
    assert exc.value.max_allowed == 100_000
```

### Backend Integration Tests

```python
# tests/integration/test_export_endpoints.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_export_sales_csv_success(client: AsyncClient, auth_headers):
    """Test successful CSV export via API"""
    response = await client.get(
        "/api/reports/sales/export?format=csv&start_date=2026-01-01&end_date=2026-01-31",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/csv"
    assert "attachment" in response.headers["Content-Disposition"]
```

### Frontend Component Tests

```typescript
// tests/components/charts/LineChart.test.tsx

import { render, screen } from '@testing-library/react';
import { SalesLineChart } from '@/components/charts/LineChart';

describe('SalesLineChart', () => {
  it('renders chart with correct data', () => {
    const data = [
      { date: '2026-01-01', revenue: 1250.50, profit: 450.25, vat: 125.05 },
      { date: '2026-01-02', revenue: 1380.75, profit: 520.60, vat: 138.08 }
    ];
    
    render(<SalesLineChart data={data} />);
    
    expect(screen.getByText('Revenue')).toBeInTheDocument();
  });
  
  it('displays decimal precision in tooltips', () => {
    // Test tooltip formatter preserves 4 decimal places
  });
});
```

## Running the Application

### Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Start Frontend

```bash
cd frontend
npm run dev
```

### Access Application

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/api/docs
- Export endpoints: http://localhost:8000/api/reports/{report}/export
- Dashboard endpoints: http://localhost:8000/api/dashboard/{type}

## Verification Checklist

### Backend Verification

- [ ] Export CSV generates with <10k rows
- [ ] Export XLSX generates with <50k rows
- [ ] Export PDF generates with correct formatting
- [ ] Row limits enforced (400 error on excess)
- [ ] Rate limiting works for large exports
- [ ] WebSocket progress messages sent
- [ ] Cancellation stops export generation
- [ ] Dashboard data returns <1000 points
- [ ] Decimal precision maintained end-to-end

### Frontend Verification

- [ ] Dashboards render with Recharts
- [ ] Date range filters work without reload
- [ ] Tooltips show 4 decimal places
- [ ] Export buttons download files
- [ ] Progress indicator shows for long exports
- [ ] Cancel button stops export
- [ ] Error messages display for limit violations
- [ ] Charts handle empty data gracefully

## Common Issues

### Issue: Decimal precision lost in CSV

**Solution**: Use `float_format='%.4f'` in pandas `to_csv()`

```python
df.to_csv(output, float_format='%.4f', index=False)
```

### Issue: Chart doesn't render with 1000+ points

**Solution**: Data point limit enforced. Suggest narrower date range to user.

### Issue: Export timeout on large files

**Solution**: Increase timeout or reduce date range. Consider async generation for >50k rows.

### Issue: WebSocket progress not updating

**Solution**: Verify WebSocket connection established and export_id matches.

## Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| CSV export (10k rows) | <30s | End-to-end |
| XLSX export (50k rows) | <30s | End-to-end |
| PDF export (10k rows) | <30s | End-to-end |
| Dashboard render | <3s | Initial load |
| Dashboard filter update | <2s | After filter change |
| Progress update latency | <500ms | WebSocket message |

## Next Steps

1. Run `/speckit.tasks` to generate detailed task breakdown
2. Implement Sprint 1 backend tasks (Days 1-3)
3. Implement Sprint 2 backend tasks (Days 4-6)
4. Implement Sprint 3 frontend tasks (Days 7-9)
5. Run full integration test suite
6. Deploy to staging environment