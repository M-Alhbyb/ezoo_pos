# ezoo_pos Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-19

## Active Technologies
- Python 3.11 (backend), TypeScript/Next.js 14 (frontend) + FastAPI 0.109, SQLAlchemy async 2.0, Pydantic 2.5, React 18, TailwindCSS 3.4 (002-quick-fee-buttons)
- PostgreSQL (sole source of truth per constitution) (002-quick-fee-buttons)
- Python 3.11 (backend), TypeScript/Next.js 14 (frontend) + FastAPI 0.109, SQLAlchemy async 2.0, Pydantic 2.5, React 18, TailwindCSS 3.4, pandas (CSV/XLSX), WeasyPrint or ReportLab (PDF), Recharts (frontend charts) (003-export-visualization-dashboards)
- PostgreSQL (via existing SQLAlchemy async models) (003-export-visualization-dashboards)
- TypeScript 5, Next.js 14 (existing) + React 18, TailwindCSS 3.4, Recharts (existing) (004-frontend-completion-arabic)
- PostgreSQL (unchanged - frontend only) (004-frontend-completion-arabic)
- Python 3.11 + FastAPI 0.109, SQLAlchemy async 2.0, Pydantic 2.5, PostgreSQL (005-partner-profit-tracking)
- Node.js 20+, Python 3.11 + Electron, electron-builder, uvicorn, Next.js (007-electron-desktop-app)
- SQLite (local, via SQLAlchemy) (007-electron-desktop-app)

- Python 3.11 (backend), TypeScript/Next.js 14 (frontend) + FastAPI (backend), Next.js 14 App Router (frontend), SQLAlchemy async (ORM), Alembic (migrations), Pydantic (validation), WebSocket (real-time updates) (001-core-pos-products-inventory)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11 (backend), TypeScript/Next.js 14 (frontend): Follow standard conventions

## Recent Changes
- 007-electron-desktop-app: Added Node.js 20+, Python 3.11 + Electron, electron-builder, uvicorn, Next.js
- 006-partner-profit-sharing: Added Python 3.11 + FastAPI 0.109, SQLAlchemy async 2.0, Pydantic 2.5
- 005-partner-profit-tracking: Added Python 3.11 + FastAPI 0.109, SQLAlchemy async 2.0, Pydantic 2.5, PostgreSQL


## Lessons Learned (002-quick-fee-buttons)

**Pattern: Settings Key-Value for Configuration**
- Use existing `settings` table with composite keys for feature configuration
- Key format: `{feature}_{entity_id}_{sub_entity}` (e.g., `fee_presets_1_shipping`)
- JSON serialization for list/array values
- Reuses existing infrastructure, no schema changes required

**Pattern: WebSocket Broadcasting for Real-time Updates**
- Extend existing `ConnectionManager` with feature-specific broadcast methods
- Follow stock update pattern: `broadcast_{feature}_update(data)`
- Frontend WebSocket listener updates local state on `preset_updated` event
- Automatic reconnection on WebSocket close

**Pattern: Decimal Serialization in Pydantic**
- Use `json_encoders = {Decimal: float}` in Pydantic schema Config
- Ensures proper JSON serialization for monetary values
- Frontend receives numbers, not strings

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
