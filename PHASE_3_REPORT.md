# Phase 3 Report — PyInstaller on Windows

**Date:** 2026-07-25
**Commit:** `9618005` — `phase-3: PyInstaller backend packaging`
**Platform:** Linux (code changes); Windows required for actual build/test

---

## What changed

### 6.1 — Port as a parameter (`backend/main.py:146-150`)

- `__main__` block now reads `EZOO_PORT` env var (default `8001`)
- Host changed from `0.0.0.0` to `127.0.0.1`
  - Prevents unauthenticated API exposure to the local network
  - Avoids Windows Firewall prompt on first launch
- Added `log_level='info'`

This is the fix for bug #2 in §1.3 of the plan (port mismatch between Electron and backend). Electron will set `EZOO_PORT` when spawning the backend process (Phase 4 work).

### 6.2 — Font/image paths (`backend/app/modules/reports/export_service.py`)

- Added `from app.core.paths import resource_path` (line 23)
- Added top-level `import os` (line 2)
- `FONT_DIR` now uses `resource_path("app/static/fonts")` instead of hardcoded `/usr/share/fonts/truetype`
- `_register_arabic_fonts()` uses `resource_path("app/static/fonts")` instead of 3-level `os.path.dirname` navigation
- `get_asset_path()` uses `resource_path("app/static/images")` instead of `os.path.dirname` navigation

**Why this matters:** Under PyInstaller, `__file__` points inside the bundle temp directory. Without `resource_path()`, the app would look for fonts in a non-existent system path, causing Arabic PDF generation to fail silently (no exception, but missing/boxed glyphs).

### 6.3 — PyInstaller spec file (`backend/ezoo-pos.spec`)

Created from scratch. Key design decisions:

| Aspect | Choice | Why |
|--------|--------|-----|
| Mode | `--onedir` via `COLLECT` | `--onefile` extracts ~250 MB to `%TEMP%` on every launch: slow, antivirus-trigger |
| Entry point | `main.py` | Single entry, no `__main__.py` confusion |
| `console` | `True` (debug) | Set to `False` for production build |
| Datas | `app/static`, `alembic`, `alembic.ini`, `../frontend/out` | Fonts+images, migrations, config, frontend bundle |
| Data files | `reportlab` AFM metrics, `arabic_reshaper` | Needed at runtime for PDF generation |
| Hidden imports | aiosqlite, sqlite dialect, uvicorn internals, arabic_reshaper, bidi, xlsxwriter | PyInstaller can't trace these through dynamic imports |
| Excludes | tkinter, matplotlib, pandas, pytest, watchfiles, IPython | Not needed in production; reduces binary size |

Deleted the root-level `ezoo-pos.spec` which was a broken `--onefile` config with incorrect data paths and missing hidden imports.

---

## What still needs to happen on Windows

The code changes are complete, but **Phase 3 acceptance criteria require a Windows build** (§6.4):

1. `cd backend && pyinstaller ezoo-pos.spec --clean --noconfirm`
2. `dist\ezoo-pos\ezoo-pos.exe`
3. Exercise all 7 checks from §6.4:
   - `/health` endpoint
   - `%APPDATA%\EZOO POS\ezoo_pos.db` has `alembic_version`
   - Frontend loads at `/`
   - API works at `/api/products`
   - **Arabic invoice PDF** — visually verify joined letters
   - XLSX export
   - WebSocket stock updates

**The Arabic invoice PDF is the highest-risk item.** It combines bundled TTF fonts, `arabic-reshaper`, and `python-bidi`. A PDF that generates without exception can still render Arabic as reversed or isolated forms.

---

## Discrepancies from plan

None. The plan's §6.1, §6.2, and §6.3 match the actual file locations and code structure:
- `export_service.py` font/image paths were at the locations described
- `main.py` `__main__` block was at the expected location
- `ezoo-pos.spec` existed at root (plan said to rewrite; it was root-level, not `backend/`)

---

## Ruff status

All 38 ruff findings are **pre-existing** in the codebase. No new issues introduced by Phase 3 changes. The existing findings are:
- `I001` import sorting (pre-existing)
- `F401` unused imports: `uuid`, `canvas`, `ExportResponse` (pre-existing)
- `F811` `canvas` parameter shadowing module import in `draw_report_header`/`draw_report_footer` (pre-existing, intentional)
- `E501` line length violations (pre-existing)
- `UP045` `Optional[X]` → `X | None` suggestions (pre-existing)
- `B008` `Depends()` in default arg (pre-existing, FastAPI pattern)
- `E712` comparison to `True` (pre-existing)

---

## Next phase

Phase 4 — Electron and the installer. This is the next step and must be done on Windows. It involves:
- Rewriting `electron/src/main.js` (spawn one child, find free port, set `DATABASE_PATH`)
- Configuring `electron-builder.yml` for NSIS target
- Testing the full installer flow
