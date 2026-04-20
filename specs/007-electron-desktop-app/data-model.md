# Data Model: Electron Desktop App

## Overview

This feature wraps existing systems in Electron. The data model is inherited from the existing backend.

## Existing Data (from Backend)

The desktop application uses the same data models as the existing FastAPI backend:

- **Products**: id, name, base_price, selling_price, stock
- **Sales**: id, created_at, items, fees, vat, total
- **Inventory**: product_id, quantity, reason, timestamp
- **Partners**: id, name, invested_amount, profit_percentage
- **Expenses**: id, name, amount, type, frequency
- **Settings**: key, value

## Database Change

| Aspect | Before | After |
|--------|--------|-------|
| Engine | PostgreSQL | SQLite |
| Host | Remote/local PostgreSQL | Local file |
| Connection | TCP | File-based |

## New Desktop-Specific Data

| Entity | Purpose | Storage |
|--------|---------|---------|
| App Log | Startup/runtime logs | File (app data) |
| Window State | Maximize/fullscreen preference | electron-store |

## Entity Relationships

No new relationships introduced. The desktop wrapper:
- Does not modify backend data model
- Does not add new entities
- Does not change business logic

## Notes

- SQLite supports DECIMAL type via SQLAlchemy
- Database file created on first app launch
- Database stored in user's app data directory