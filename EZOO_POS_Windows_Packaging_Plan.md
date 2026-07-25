# EZOO POS — Windows Single-Installer Migration Plan

**Version:** 1.0
**Date:** 2026-07-25
**Basis:** Codebase audit report (19,081 backend LOC / 16,001 frontend LOC / 27 Alembic migrations)
**Target:** One signed `EZOO-POS-Setup.exe`. User double-clicks, app opens. No Python, no Node, no PostgreSQL, no cmd, no admin rights.

---

## 0. How to use this document

This plan is written to be executed by an AI coding agent, one phase per session.

**Rules for the agent:**

1. Work on **one phase at a time**. Do not start a later phase because it looks easy.
2. Every phase ends with an **Acceptance Criteria** block. All items must pass before moving on. If one fails, stop and report — do not work around it.
3. Do not refactor code outside the file list for the current phase.
4. Commit at the end of each phase with the phase number in the message (`phase-1: database hardening`).
5. Where this plan gives code, treat it as the intended shape, not necessarily literal text — adapt to the actual surrounding code, but do not change the behaviour described.
6. If reality contradicts this document (a file isn't where it's said to be, a bug is already fixed), **report the discrepancy** rather than silently deviating.

**Rules for the human:**

- Take a full copy of `backend/ezoo_pos.db` before Phase 1. Store it outside the repo.
- Phases 0–2 can be done on Linux/macOS. **Phases 3–5 must be done on Windows** (or in CI on `windows-latest`).

---

## 1. Current state: what the audit actually found

Three findings reshape the whole project.

### 1.1 The database is already SQLite

`backend/app/core/database.py:31-37` builds `sqlite+aiosqlite:///` URLs from a `DATABASE_PATH` env var. No PostgreSQL driver is imported anywhere in `app/`. All 27 Alembic migrations already carry `if bind.dialect.name == "postgresql"` guards with SQLite fallback paths, and `alembic/env.py:48,66` already sets `render_as_batch=True`.

**The Postgres→SQLite migration is done.** It was completed at some earlier point and the surrounding scaffolding (`.env.example`, `setup_extensions.sql`, `asyncpg`, `psycopg2-binary`, `tests/conftest.py`) was never updated to match. Everything Postgres-shaped in the repo is now vestigial.

### 1.2 The money handling is already correct

All financial arithmetic is Python `Decimal` with `ROUND_HALF_UP` in `app/core/calculations.py`. SQL touches money only via `func.sum()` aggregation. SQLAlchemy's SQLite dialect quantizes floats back to `Decimal` at the declared scale on read, so single-value round trips are exact.

At 200 orders/day, float accumulation error across a year of `SUM` aggregation is ~1e-9 against totals in the millions — nine orders of magnitude below the 0.005 needed to flip a rounded penny.

**Decision: do not convert the 27 `Numeric(12,2)` columns to integer minor units.** The conversion would touch every monetary column, every aggregation site and every serializer, to fix a problem that does not exist here. Instead, Phase 0 adds one guard test that will fail loudly if this assumption ever breaks.

The `float()` casts in `export_service.py:744,753-756,847,855-858`, `api/routes/dashboard.py:60-63` and `reports/routes.py:427-441` are all on the display/export path after rounding. They are fine and should be left alone.

### 1.3 The install failed because of four wrong strings

| # | Bug | Location | Effect |
|---|-----|----------|--------|
| 1 | `backend/dist/ezoo-pos` is a **Linux ELF binary**, 252 MB | built by `ezoo-pos.spec` on Linux | Electron spawns a file Windows cannot execute |
| 2 | Port mismatch: Electron polls **8000**, backend serves **8001** | `electron/src/main.js:9` vs `backend/main.py:126` | Health check times out after 60s → error screen |
| 3 | Electron sets `DATABASE_URL`; backend only reads `DATABASE_PATH` | `electron/src/main.js` vs `app/core/database.py:31` | DB lands relative to CWD, which is read-only when installed |
| 4 | `electron-builder.yml` target is `dir`, not `nsis` | `electron/electron-builder.yml:15` | No installer is produced at all |

None of these are architectural. This is why the effort estimate is days, not weeks.

---

## 2. Target architecture

```
EZOO-POS-Setup.exe  (NSIS, perMachine: false → %LOCALAPPDATA%, no UAC)
└── EZOO POS.exe                        Electron main process
    ├── picks a free TCP port
    ├── sets DATABASE_PATH → %APPDATA%\EZOO POS\ezoo_pos.db
    ├── spawns  resources/backend/ezoo-pos.exe   (PyInstaller --onedir)
    │           └── FastAPI + uvicorn
    │               ├── /api/**            all 11 routers
    │               ├── /ws/stock-updates  WebSocket
    │               └── /                  StaticFiles(frontend out/, html=True)
    ├── polls http://127.0.0.1:<port>/health
    └── loadURL('http://127.0.0.1:<port>/')
```

**One runtime process besides Electron. No Node at runtime. No separate frontend server.**

### 2.1 The one design change: FastAPI serves the frontend

Rather than loading the static export over `file://`, mount it in FastAPI at `/` and have Electron load `http://127.0.0.1:<port>/`.

This is worth doing because it removes four problems at once:

- **CORS disappears.** A `file://` page sends `Origin: null`, which `allow_origins=["http://localhost:3000"]` (`config.py:19`) rejects.
- **All 83 `fetch()` call sites keep working unchanged.** They currently use relative `/api/...`, which only resolves because of the Next.js rewrite at `next.config.mjs:8`. Same-origin serving preserves that. The alternative — injecting a runtime API base URL — means editing 83 sites across `lib/api/*.ts` and mixed direct-`fetch` files.
- **The WebSocket URL becomes derivable** from `window.location` instead of the hardcoded `ws://localhost:8001/ws/stock-updates` at `lib/websocket-client.ts:38`.
- **`startFrontend()` is deleted entirely** (`electron/src/main.js:141-181`). No Node binary shipped (~40 MB saved), one fewer child process to orphan, one fewer 60-second health poll on startup.

### 2.2 Decisions register

| Decision | Choice | Rationale |
|---|---|---|
| Database | SQLite, stays | Single register, ~200 orders/day, ~50k rows/year |
| Money representation | `Numeric(12,2)`, unchanged | §1.2 — Python `Decimal` throughout; error is 9 orders of magnitude below significance |
| Frontend delivery | Next.js `output: 'export'`, served by FastAPI | §2.1 |
| Dynamic routes | Converted to query params | Static export cannot prerender unknown IDs |
| Backend packaging | PyInstaller `--onedir` | `--onefile` unpacks to temp on every launch: slow, antivirus-prone |
| Installer | electron-builder NSIS, `perMachine: false` | Installs to `%LOCALAPPDATA%`, no UAC prompt |
| Backend port | Free ephemeral port chosen by Electron | Removes the 8000/8001 class of bug permanently |
| DB location | `%APPDATA%\EZOO POS\` | Install dir may be read-only |
| pandas | Removed | Used only for `to_excel`; `xlsxwriter` already a direct dep; worst PyInstaller citizen in the tree |
| Migrations | `alembic upgrade head` at startup | Replaces `create_all`, which cannot be upgraded (§4.2) |
| `.with_for_update()` | Accepted as a no-op | Single writer + `StaticPool`; see §4.4 |
| Authentication | Out of scope, tracked | See Phase 6 |

---

## 3. Phase 0 — Cleanup and a working safety net

**Goal:** a runnable test suite and a dependency tree worth packaging.
**Effort:** ~0.5 day.
**Platform:** any.
**Why first:** the test suite is the gate for every later phase, and it currently cannot run at all.

### 3.1 Make the tests run against SQLite

`tests/conftest.py:23` hardcodes:

```python
TEST_DATABASE_URL = "postgresql+asyncpg://pasha:pshpsh00@localhost:5432/ezoo_pos_test"
```

So all 23 test files across `tests/unit/`, `tests/integration/`, `tests/concurrency/`, `tests/invariants/`, `tests/performance/` and `tests/modules/reports/` currently exercise a database engine the application does not use. They are simultaneously unrunnable and unrepresentative.

Replace with a per-test temp-file SQLite database. Use a **file**, not `:memory:` — `StaticPool` plus async sessions plus `VACUUM INTO` behave differently in memory, and a file matches production.

```python
# tests/conftest.py
import os, tempfile, pytest, pytest_asyncio
from pathlib import Path

@pytest.fixture
def db_path(tmp_path) -> str:
    return str(tmp_path / "test_ezoo.db")

@pytest_asyncio.fixture
async def engine(db_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", db_path)
    import app.core.database as db
    db._async_engine = None          # reset module-level singletons
    db._async_session_local = None
    from app.core.database import get_engine, Base
    eng = get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()
```

Note the singleton reset — `database.py:39-40` caches `_async_engine` and `_async_session_local` at module level, so without clearing them every test after the first reuses the first test's database.

**Expect this step to surface real bugs.** Tests that have never run against SQLite will fail for legitimate reasons. Triage each one:

- genuine SQLite behavioural difference → fix the application code
- test asserts a Postgres-only guarantee → see §3.2
- test is stale relative to current code → fix or delete, do not skip silently

Delete `backend/test_ezoo.db` from the repo and add `*.db` to `.gitignore`.

### 3.2 Mark the concurrency tests honestly

`tests/concurrency/` tests row-level locking. `.with_for_update()` at `inventory/service.py:331` and `partner_profit_service.py:59,73` is a **silent no-op on SQLite** — SQLAlchemy emits nothing and no error is raised.

Do not delete these tests. Mark them:

```python
pytestmark = pytest.mark.skip(
    reason="SELECT FOR UPDATE is a no-op on SQLite. Single-writer deployment "
           "serialises writes instead. Re-enable if the DB backend changes."
)
```

A skipped test with a reason is documentation. A passing test that asserts a guarantee the engine does not provide is a liability.

### 3.3 Add the money guard test

This is the one thing that replaces the integer-minor-units migration. It must be convincing, not decorative.

```python
# tests/invariants/test_decimal_aggregation.py
import random
from decimal import Decimal
from sqlalchemy import select, func

async def test_sql_sum_matches_python_decimal_sum(session):
    """SQLite stores Numeric as float. Prove that SUM over a year of sales
    still matches exact Decimal arithmetic to the penny."""
    random.seed(1)
    values = [Decimal(random.randrange(1, 10_000_00)) / 100 for _ in range(50_000)]
    # ... insert values as Sale.grand_total rows ...
    sql_total = (await session.execute(select(func.sum(Sale.grand_total)))).scalar()
    assert Decimal(str(sql_total)).quantize(Decimal("0.01")) == sum(values)
```

Also assert round-trip fidelity on the awkward cases — values ending in `.005`, `.015`, `.995`, and the `Numeric(5,2)` rate columns (`vat_rate`, `share_percentage`).

If this ever fails, the integer-minor-units migration becomes necessary. It will not fail at this scale.

### 3.4 Split the dependencies

PyInstaller currently bundles pytest, pytest-asyncio, pytest-cov, httpx and testcontainers into the shipped binary. Split:

**`requirements.txt` (runtime — what gets packaged):**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy[asyncio]==2.0.25
alembic==1.13.1
aiosqlite==0.19.0
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0
websockets==12.0
python-multipart==0.0.6
python-dotenv==1.0.0
ReportLab==4.0.7
xlsxwriter==3.2.0
slowapi==0.1.9
arabic-reshaper==3.0.0
python-bidi==0.4.2
```

**`requirements-dev.txt`:**
```
-r requirements.txt
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0
pyinstaller==6.*
ruff
```

Changes: `asyncpg` and `psycopg2-binary` **removed** (unused, C extensions, ~40 MB in the binary). `testcontainers` **removed** (in requirements but never used — `conftest.py` hardcodes a connection string instead). `pandas` **removed** (see §3.5). `aiosqlite` and `pyinstaller` now **pinned** — they were unpinned.

### 3.5 Remove pandas

`app/modules/reports/export_service.py` uses pandas only to reach `DataFrame.to_excel()`. `xlsxwriter==3.2.0` is already a direct dependency and is what pandas calls underneath.

Rewrite the XLSX generation paths to use `xlsxwriter` directly. This is a mechanical change in one 927-line file. The win: roughly 40–50 MB off the shipped binary, and pandas is the single most PyInstaller-hostile package in the tree (runtime data files, plugin discovery, hook fragility).

Note that `requirements.txt:31` pins `pandas==3.0.2`, which is a suspicious version number — check whether this is even installable. If pandas removal turns out to be more than a day's work, defer it to Phase 3 and accept the binary size; but do not defer it silently.

### 3.6 Delete the Postgres vestiges

| Delete | Reason |
|---|---|
| `backend/setup_extensions.sql` | `CREATE EXTENSION pg_trgm` — unused by any code path |
| `backend/list_tables.py` | Queries `pg_catalog.pg_tables`; Postgres-only, utility script |
| `backend/clear_data.py` | `to_regclass`, `TRUNCATE ... CASCADE`; Postgres-only |
| `backend/dist/ezoo-pos` | 252 MB Linux ELF binary committed to the repo |

If `clear_data.py` is genuinely used in development, rewrite it against SQLite (`DELETE FROM` + `PRAGMA foreign_keys=OFF` around it) rather than deleting. If nobody remembers using it, delete.

Add to `.gitignore`: `dist/`, `build/`, `*.db`, `.venv/`, `venv/`, `out/`.

### 3.7 Fix `.env.example`

Currently line 2 reads `DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ezoo_pos`, which the application does not read and which describes an engine it does not use. This is what makes a new developer install PostgreSQL for no reason.

```
# Path to the SQLite database file.
# Leave unset in production — defaults to %APPDATA%\EZOO POS\ezoo_pos.db on
# Windows and ~/.local/share/ezoo-pos/ezoo_pos.db elsewhere.
# DATABASE_PATH=ezoo_pos.db

APP_NAME=EZOO POS
APP_VERSION=1.0.0

# Only used by `next dev`; irrelevant in the packaged app, which is same-origin.
CORS_ORIGINS=["http://localhost:3000"]

CSV_MAX_ROWS=100000
XLSX_MAX_ROWS=50000
PDF_MAX_ROWS=10000
EXPORT_RATE_LIMIT_THRESHOLD=5000
EXPORT_RATE_LIMIT_PER_HOUR=10
DASHBOARD_MAX_POINTS=1000
EXPORT_TIMEOUT_SECONDS=30
DASHBOARD_TIMEOUT_SECONDS=3
```

### 3.8 Add a ruff config

`.ruff_cache/` exists with three different ruff versions but there is no `ruff.toml` or `[tool.ruff]` section anywhere. Someone ran ruff ad hoc. Pin it:

```toml
# backend/pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

### Acceptance criteria — Phase 0

- [ ] `pytest` runs to completion with **zero** PostgreSQL processes on the machine
- [ ] Every test either passes or is skipped with an explicit written reason
- [ ] `test_decimal_aggregation.py` passes with 50,000 rows
- [ ] `pip install -r requirements.txt` in a clean venv installs **no** `asyncpg`, `psycopg2`, `pandas`, `pytest`, `testcontainers`
- [ ] XLSX export produces a file openable in Excel, with pandas uninstalled
- [ ] Clean venv size is under **150 MB** (down from 313 MB)
- [ ] `ruff check .` passes, or every remaining finding is deliberate
- [ ] `git grep -il postgres -- ':!specs/' ':!*.md'` returns only the guarded dialect branches inside `alembic/versions/`

---

## 4. Phase 1 — Database hardening

**Goal:** the SQLite setup becomes correct and upgradable, and lives somewhere Windows allows writing.
**Effort:** ~1 day.
**Platform:** any.
**Prerequisite:** Phase 0 green, and a backup copy of `ezoo_pos.db` stored outside the repo.

### 4.1 Enforce foreign keys (do the orphan check first)

SQLite disables foreign key enforcement **per connection** by default, and `database.py` registers no connect listener. Every `ForeignKey` in all 17 tables is therefore currently decorative — the schema declares them, the engine ignores them, and orphaned rows can be written without error.

**Before enabling enforcement, audit the existing data.** Turning this on will start rejecting writes that previously succeeded, and may reveal existing orphans.

```python
# scripts/check_orphans.py
import sqlite3, sys
con = sqlite3.connect(sys.argv[1])
con.execute("PRAGMA foreign_keys=ON")
rows = con.execute("PRAGMA foreign_key_check").fetchall()
for table, rowid, parent, fkid in rows:
    print(f"ORPHAN  {table}  rowid={rowid}  -> missing parent in {parent}")
print(f"\n{len(rows)} violation(s)")
```

Run against the production DB and the dev DB. Resolve every violation before proceeding — deleting orphans or reinstating parents, decided case by case. `partner_wallet_transactions`, `sale_items` and `supplier_ledger` are the likeliest sites, since they are written by multi-step service flows.

Then add the listener. It must be attached to the engine's connection event, not executed once at startup, because pragmas are per-connection:

```python
# app/core/database.py
from sqlalchemy import event

def _install_pragmas(sync_engine) -> None:
    @event.listens_for(sync_engine, "connect")
    def _set_pragmas(dbapi_conn, _record):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")     # concurrent reads during writes
        cur.execute("PRAGMA foreign_keys=ON")      # off by default — this is the fix
        cur.execute("PRAGMA busy_timeout=5000")    # wait instead of failing on lock
        cur.execute("PRAGMA synchronous=NORMAL")   # safe under WAL, much faster
        cur.close()
```

Call it on both engines — `get_engine()` needs `_install_pragmas(_async_engine.sync_engine)`, and the sync engine used for migrations needs it directly.

`synchronous=NORMAL` is safe specifically because WAL is enabled; under WAL a crash cannot corrupt the database, it can only lose the most recent transaction. Do not set `synchronous=OFF`.

### 4.2 Replace `create_all` with `alembic upgrade head`

This is the most important fix in the phase, because it is the one that breaks *future* releases rather than the current one.

Right now `main.py:76-83` startup calls `init_db()`, which runs `Base.metadata.create_all()` (`database.py:78`). That builds the schema directly from the models and **never writes an `alembic_version` row**. So the 27-migration chain can never execute against a database the app created — Alembic sees no version, assumes an empty database, and tries to `CREATE TABLE` tables that already exist.

Consequence: the first time you ship a schema change to a machine with real data, the update fails and the shop cannot open.

```python
# app/core/migrations.py
import os, sys
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from app.core.paths import resource_path
from app.core.database import get_sync_database_url

def run_migrations() -> None:
    cfg = Config(resource_path("alembic.ini"))
    cfg.set_main_option("script_location", resource_path("alembic"))
    cfg.set_main_option("sqlalchemy.url", get_sync_database_url())

    engine = create_engine(get_sync_database_url())
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()

    if tables and "alembic_version" not in tables:
        # Legacy DB built by create_all(): schema exists but is unversioned.
        # Adopt it at head rather than replaying migrations over live tables.
        command.stamp(cfg, "head")

    command.upgrade(cfg, "head")
```

**Caveat to state explicitly:** stamping `head` asserts that the existing schema matches the newest migration. That is true if the DB was built by `create_all()` from the current models. If an old database was built from *older* models, stamping lies and later migrations will fail on missing columns. This is why the backup in the prerequisites is mandatory. If in doubt for a given database, compare `PRAGMA table_info` against the models before stamping.

Then rewrite startup:

```python
@app.on_event("startup")
async def startup_event():
    ensure_data_dir()        # §4.3
    backup_database()        # §4.4
    run_migrations()         # replaces init_db()
    logger.info("Database ready at %s", settings.database_path)
```

**Delete `seed_data()`** (`database.py:88-104`). Its raw INSERT of Cash / M-PESA / Card is now redundant: migrations `098407b39884_seed_payment_methods_and_settings.py` and `t009_seed_default_fee_presets.py` already seed the same data, idempotently, with dialect-appropriate UUID generation. Keeping both risks duplicate payment methods.

While here: verify the seeded payment methods are intentional. The audit reports currency as **GBP** but the seed list includes **M-PESA** (an East African mobile money service). One of the two is probably wrong for this business.

### 4.3 Move the data to `%APPDATA%`

`app/core/config.py:7` defaults the database to a path relative to `backend/`. When installed to `%LOCALAPPDATA%\Programs\EZOO POS\`, that directory may be read-only and is wiped by updates.

```python
# app/core/paths.py
import os, sys
from pathlib import Path

APP_DIR_NAME = "EZOO POS"

def user_data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / APP_DIR_NAME

def default_database_path() -> str:
    return str(user_data_dir() / "ezoo_pos.db")

def ensure_data_dir() -> None:
    (user_data_dir() / "backups").mkdir(parents=True, exist_ok=True)
    (user_data_dir() / "logs").mkdir(parents=True, exist_ok=True)

def resource_path(rel: str) -> str:
    """Resolve a bundled read-only resource, PyInstaller-aware."""
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        base = Path(__file__).resolve().parents[2]   # backend/
    return str(Path(base) / rel)
```

`DATABASE_PATH` remains an override (Electron sets it, dev can set it), but the default is now correct on all three platforms with no configuration.

`resource_path()` is used again in Phase 3 for fonts, the Alembic directory and the frontend bundle — write it once, here.

### 4.4 Automatic backups

The entire business is one file. That is excellent for backup and terrible for a single point of failure. Mitigate at startup:

```python
# app/core/backup.py
import sqlite3
from datetime import date
from app.core.paths import user_data_dir
from app.core.config import settings

KEEP = 30

def backup_database() -> None:
    src = settings.database_path
    if not os.path.exists(src):
        return
    dest_dir = user_data_dir() / "backups"
    dest = dest_dir / f"ezoo_pos-{date.today():%Y-%m-%d}.db"
    if dest.exists():
        return                       # already backed up today
    con = sqlite3.connect(src)
    try:
        con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        con.execute("VACUUM INTO ?", (str(dest),))
    finally:
        con.close()
    for old in sorted(dest_dir.glob("ezoo_pos-*.db"))[:-KEEP]:
        old.unlink()
```

Use `VACUUM INTO`, **not** a file copy — under WAL, a raw copy of the `.db` file without the `-wal` sidecar can be missing committed transactions. Never let a backup failure prevent startup: wrap the call in `try/except` and log.

Add a "Backup now" and "Open backups folder" action in Settings so the owner can put a copy on a USB stick before doing anything risky.

### 4.5 Timezone note

All models use `DateTime(timezone=True)` (`database.py:14-22`), but SQLite has no native timezone-aware type — offsets are not stored. If any reporting logic relies on timezone offsets rather than naive local time, it is already silently wrong and Phase 0's tests may reveal it. For a single shop in a single timezone this is acceptable; record it as a known limitation rather than fixing it.

### Acceptance criteria — Phase 1

- [ ] `PRAGMA foreign_key_check` returns zero rows on both the dev and production databases
- [ ] `PRAGMA foreign_keys` returns `1` on a connection taken from the app's engine (assert this in a test)
- [ ] `PRAGMA journal_mode` returns `wal`
- [ ] Inserting a `sale_item` with a nonexistent `sale_id` now raises `IntegrityError` (add a test)
- [ ] Starting against an **empty** directory creates the DB in `%APPDATA%`/XDG dir and reaches `alembic_version` = head
- [ ] Starting against a **copy of the existing** `ezoo_pos.db` stamps head, upgrades cleanly, and all data is still readable through the UI
- [ ] Starting twice in a row does not duplicate payment methods or fee presets
- [ ] A dated `.db` file appears in `backups/` on first run and does not reappear on second run the same day
- [ ] `seed_data()` no longer exists in the codebase
- [ ] Full test suite still green

---

## 5. Phase 2 — Static export

**Goal:** `npm run build` produces a fully static `out/` directory that works when served from any origin.
**Effort:** ~1 day.
**Platform:** any.

The audit found five blockers. Four are configuration; one is real work.

### 5.1 The four easy ones

**`next.config.mjs`** — currently `output: 'standalone'` with a rewrite and a redirect, neither of which survives static export. But `next dev` still needs the rewrite, so make it conditional:

```js
/** @type {import('next').NextConfig} */
const isExport = process.env.NEXT_OUTPUT === "export";

const nextConfig = {
  ...(isExport
    ? {
        output: "export",
        trailingSlash: true,          // /products/ -> out/products/index.html
        images: { unoptimized: true } // no Image Optimization server
      }
    : {
        async rewrites() {
          return [{
            source: "/api/:path*",
            destination: `http://127.0.0.1:${process.env.DEV_API_PORT ?? 8001}/api/:path*`
          }];
        }
      })
};

export default nextConfig;
```

Build with `NEXT_OUTPUT=export next build`. Add `"build:export": "cross-env NEXT_OUTPUT=export next build"` to `package.json` scripts.

`trailingSlash: true` matters: it makes every route emit `out/<route>/index.html`, which `StaticFiles(html=True)` resolves without any custom routing.

**The redirect** (`/partners/assignment` → `/partners/assignments`) cannot be expressed in a static export. Fix the links instead: `git grep -n "partners/assignment\b"` and correct each. If the old URL might be bookmarked, add a tiny `app/partners/assignment/page.tsx` that `router.replace`s.

**`next/image`** — used at `app/layout.tsx:18`, `components/layout/Sidebar.tsx:5`, `components/layout/Header.tsx:5`, `app/login/page.tsx:4`, with no custom loader. `unoptimized: true` handles all four. Verify the images still render at the right size; `unoptimized` skips resizing, so an oversized source file will now be shipped at full weight.

**`next/font/google`** (Inter + Cairo, `app/layout.tsx:16`) needs **no change** — it downloads and self-hosts at build time. But it downloads *at build time*, so CI needs network access during `next build`. Confirm this works in the Phase 5 workflow; if the CI runner is network-restricted, switch to `next/font/local` with the Cairo files already in `backend/app/static/fonts/`.

### 5.2 The real work: five dynamic routes

Static export cannot prerender a route whose parameter values aren't known at build time, and none of these five has `generateStaticParams`:

| Current | New | Reads ID via |
|---|---|---|
| `app/suppliers/[id]/page.tsx` | `app/suppliers/detail/page.tsx?id=` | `useSearchParams()` |
| `app/partners/[partnerId]/page.tsx` | `app/partners/detail/page.tsx?partnerId=` | `useSearchParams()` |
| `app/partners/wallet/[partnerId]/page.tsx` | `app/partners/wallet/page.tsx?partnerId=` | `useSearchParams()` |
| `app/customers/[id]/page.tsx` | `app/customers/detail/page.tsx?id=` | `useSearchParams()` |
| `app/pos/history/[saleId]/page.tsx` | `app/pos/history/detail/page.tsx?saleId=` | `useSearchParams()` |

Every one of these pages is already `"use client"` and fetches its own data client-side, so the component bodies barely change. The work is the route shape and the call sites.

Pattern:

```tsx
"use client";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function SupplierDetailInner() {
  const id = useSearchParams().get("id");
  if (!id) return <p>معرّف المورد مفقود</p>;
  // ...existing component body, unchanged...
}

// useSearchParams requires a Suspense boundary during prerender
export default function Page() {
  return (
    <Suspense fallback={<Loading />}>
      <SupplierDetailInner />
    </Suspense>
  );
}
```

The `Suspense` wrapper is not optional — `useSearchParams()` without one causes a build-time prerender error in the App Router.

Then update every navigation site. Grep for each pattern rather than trusting a list:

```bash
git grep -nE "(href|push|replace)\([^)]*(suppliers|customers|partners|history)/\$\{" frontend/
git grep -nE "\`/(suppliers|customers)/\$\{" frontend/
```

Update `<Link href={`/suppliers/${id}`}>` → `<Link href={`/suppliers/detail?id=${id}`}>` and the equivalent `router.push` calls. Missing one produces a 404 that only appears when clicked, so this needs a click-through of all five flows.

Keep the Arabic strings in `lib/constants/arabic.ts` (545 lines) as the source for any new "missing ID" messages — do not hardcode English.

### 5.3 Derive the WebSocket URL

`lib/websocket-client.ts:38` hardcodes `ws://localhost:8001/ws/stock-updates`, which is wrong once the port is ephemeral.

```ts
const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ??
  (typeof window !== "undefined"
    ? `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws/stock-updates`
    : "");
```

Same-origin derivation works in the packaged app because FastAPI serves both. In `next dev` the rewrite does **not** proxy WebSocket upgrades, so keep `NEXT_PUBLIC_WS_URL=ws://localhost:8001/ws/stock-updates` in `frontend/.env.local` for development.

Confirm the client has reconnect-with-backoff — with an ephemeral port and a backend that starts a moment after the window, the first connection attempt may lose the race.

### 5.4 Mount the export in FastAPI

Append to `main.py`, **after all routers and all other route declarations** — a `/` mount registered earlier would shadow `/api/**`:

```python
from fastapi.staticfiles import StaticFiles
from app.core.paths import resource_path

_frontend = resource_path("frontend_out")
if os.path.isdir(_frontend):
    app.mount("/", StaticFiles(directory=_frontend, html=True), name="frontend")
else:
    logger.warning("No frontend bundle at %s — API-only mode", _frontend)
```

The `isdir` guard keeps `uvicorn main:app --reload` working in development, where the frontend is served by `next dev` on :3000.

Static export emits `out/404.html`; `StaticFiles` will not use it automatically. Add an exception handler that returns it for unmatched non-`/api` GETs so a mistyped URL shows the app's own 404 rather than raw JSON.

### 5.5 Simplify development while here

Replace `setup.bat` / `run_dev.bat` / `stop_dev.bat` with one root `package.json`:

```json
{
  "scripts": {
    "dev": "concurrently -n api,web -c blue,green \"npm:dev:api\" \"npm:dev:web\"",
    "dev:api": "cd backend && uv run uvicorn main:app --reload --port 8001",
    "dev:web": "cd frontend && npm run dev",
    "setup": "cd backend && uv sync && cd ../frontend && npm install"
  }
}
```

Adopting [`uv`](https://docs.astral.sh/uv/) removes the `python -m venv` / `activate` / `pip install` sequence that `setup.bat` automates — `uv` is a single binary that installs the correct Python itself. This is developer convenience only; it does not affect the shipped installer.

### Acceptance criteria — Phase 2

- [ ] `NEXT_OUTPUT=export npm run build` completes with **zero** errors and zero "not supported with output: export" warnings
- [ ] `out/` contains an `index.html` for every route, including all five converted detail pages
- [ ] `npx serve out` on an arbitrary port: every page loads, no console errors
- [ ] All five converted pages work when reached by clicking through the UI, **and** when their URL is pasted directly into the address bar
- [ ] `git grep` finds no remaining links to the old `[id]` route shapes
- [ ] Backend serving `out/`: full click-through of POS sale → invoice PDF → partner wallet → supplier ledger → customer ledger → dashboard, with no CORS errors in the console
- [ ] WebSocket stock updates work same-origin (change stock in one window, see it update in another)
- [ ] Arabic RTL layout and the Cairo font render correctly in the built output
- [ ] `npm run dev` still works with the rewrite path

---

## 6. Phase 3 — PyInstaller on Windows

**Goal:** `backend/dist/ezoo-pos/ezoo-pos.exe` runs standalone on a Windows machine with no Python installed.
**Effort:** ~1 day, most of it iterating on missing imports and data files.
**Platform:** **Windows only.** Cross-compiling from Linux does not work — this is bug #1 from §1.3.

### 6.1 Make the port a parameter

```python
# backend/main.py
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("EZOO_PORT", "8001"))
    uvicorn.run(app, host="127.0.0.1", port=port, reload=False, log_level="info")
```

Two changes: the port comes from the environment, and the host is `127.0.0.1` rather than `0.0.0.0`. Binding `0.0.0.0` exposes an unauthenticated API (§8.1) to the entire local network and triggers a Windows Firewall prompt on first launch. Loopback avoids both.

### 6.2 Fix the font paths

`app/modules/reports/export_service.py:38-42` and `:111-112` resolve `static/fonts` and `static/images` relative to `app/`. Under PyInstaller `__file__` points inside the bundle, so these must go through `resource_path()` from Phase 1:

```python
FONT_DIR = resource_path("app/static/fonts")
IMAGE_DIR = resource_path("app/static/images")
```

This is the single most likely cause of a "works in dev, broken in the exe" failure, because it only manifests when someone prints a receipt.

### 6.3 The spec file

Rewrite `ezoo-pos.spec`:

```python
# ezoo-pos.spec
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

datas = [
    ("app/static", "app/static"),          # Cairo fonts + logo images
    ("alembic", "alembic"),                # env.py + versions/ (27 files)
    ("alembic.ini", "."),
    ("../frontend/out", "frontend_out"),   # the static export from Phase 2
]
datas += collect_data_files("reportlab")   # AFM font metrics
datas += collect_data_files("arabic_reshaper")

hiddenimports = [
    "aiosqlite",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.dialects.sqlite.aiosqlite",
    "uvicorn.lifespan.on", "uvicorn.lifespan.off",
    "uvicorn.loops.auto", "uvicorn.loops.asyncio",
    "uvicorn.protocols.http.auto", "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.logging",
    "arabic_reshaper", "bidi.algorithm",
    "xlsxwriter",
]
hiddenimports += collect_submodules("app.modules")   # routers imported dynamically

a = Analysis(
    ["main.py"],
    pathex=["."],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "matplotlib", "pandas", "pytest", "watchfiles", "IPython"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, name="ezoo-pos", console=False, ...)
coll = COLLECT(exe, a.binaries, a.datas, name="ezoo-pos")   # --onedir
```

Notes on specific entries:

- **`alembic` as data, not import.** Alembic loads `versions/*.py` from the filesystem by path, so they must exist as real files in the bundle. Including the directory as data is correct; adding them as hidden imports is not.
- **`console=False`** so no black cmd window flashes behind the app. During Phase 3 debugging, temporarily set `console=True` — you will need to see tracebacks.
- **`excludes`** — `pandas` is listed even though Phase 0 removed it, as a guard against a transitive dependency pulling it back in. `watchfiles` comes from `uvicorn[standard]` and is only used by `--reload`.
- **`--onedir` via `COLLECT`**, not `--onefile`. `--onefile` extracts ~250 MB to `%TEMP%` on every launch: slow cold start and a reliable antivirus trigger.

### 6.4 Iterate

```bat
cd backend
pyinstaller ezoo-pos.spec --clean --noconfirm
dist\ezoo-pos\ezoo-pos.exe
```

Then, in a browser, exercise **every** subsystem, because PyInstaller failures are per-code-path, not global:

| Check | URL / action | Catches |
|---|---|---|
| Startup | `http://127.0.0.1:8001/health` | missing uvicorn/sqlalchemy imports |
| Migrations | check `%APPDATA%\EZOO POS\ezoo_pos.db` has `alembic_version` | alembic data files missing |
| Frontend | `http://127.0.0.1:8001/` | `frontend_out` not bundled |
| API | `http://127.0.0.1:8001/api/products` | dialect / driver imports |
| **Arabic PDF** | create a sale, then fetch its invoice | **fonts, reshaper, bidi — the big one** |
| XLSX export | any report export | xlsxwriter data files |
| WebSocket | open two windows, change stock | websockets protocol impl |

**The Arabic invoice PDF is the highest-risk item in this phase.** It combines three fragile things — bundled TTF files resolved through `resource_path`, `arabic-reshaper`, and `python-bidi`. Open the generated PDF and confirm the Arabic letters are joined and in the right order, not reversed or rendered as isolated forms or boxes. A PDF that generates without an exception can still be visually wrong.

### 6.5 Expected size

| Component | Approx |
|---|---|
| Python + stdlib | 15 MB |
| FastAPI + uvicorn + pydantic | 25 MB |
| SQLAlchemy + alembic + aiosqlite | 20 MB |
| ReportLab + fonts | 15 MB |
| xlsxwriter, reshaper, bidi | 5 MB |
| `frontend_out/` | 5–10 MB |
| **Backend total** | **~90 MB** (from 252 MB) |
| Electron runtime | ~150 MB |
| **Installer (compressed)** | **~110–140 MB** |

If the backend comes out much larger than 90 MB, something excluded is still being pulled in — check `build/ezoo-pos/xref-*.html` for the culprit.

### Acceptance criteria — Phase 3

- [ ] `ezoo-pos.exe` runs on a Windows machine (or clean VM) with **no Python installed**
- [ ] All seven checks in the §6.4 table pass
- [ ] The Arabic invoice PDF is visually correct — joined letters, correct direction
- [ ] With `EZOO_PORT=9123` set, the app serves on 9123
- [ ] The database is created under `%APPDATA%\EZOO POS\`, not next to the exe
- [ ] Running from a **read-only** directory still works (proves nothing writes to the install dir)
- [ ] No console window appears with `console=False`
- [ ] `dist/ezoo-pos/` is under 120 MB

---

## 7. Phase 4 — Electron and the installer

**Goal:** a double-clickable installer producing a working desktop app.
**Effort:** ~0.5–1 day.
**Platform:** Windows.

### 7.1 Rewrite the main process

The existing `electron/src/main.js` is 362 lines with two spawn-and-poll cycles. It becomes roughly half that: one child process, one health poll.

```js
const { app, BrowserWindow } = require("electron");
const { spawn } = require("child_process");
const net = require("net");
const path = require("path");
const log = require("electron-log");

let backend = null;
let port = null;

function findFreePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.unref();
    srv.on("error", reject);
    srv.listen(0, "127.0.0.1", () => {
      const { port } = srv.address();
      srv.close(() => resolve(port));
    });
  });
}

function backendExe() {
  return app.isPackaged
    ? path.join(process.resourcesPath, "backend", "ezoo-pos.exe")
    : path.join(__dirname, "..", "..", "backend", "dist", "ezoo-pos", "ezoo-pos.exe");
}

async function startBackend() {
  port = await findFreePort();
  const dbPath = path.join(app.getPath("appData"), "EZOO POS", "ezoo_pos.db");

  backend = spawn(backendExe(), [], {
    env: { ...process.env, EZOO_PORT: String(port), DATABASE_PATH: dbPath },
    cwd: path.dirname(backendExe()),
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true,
  });

  backend.stdout.on("data", d => log.info("[api]", d.toString().trim()));
  backend.stderr.on("data", d => log.error("[api]", d.toString().trim()));
  backend.on("exit", code => {
    log.error("backend exited", code);
    backend = null;
  });

  await waitForHealth(port, 60_000);
}
```

Four things this fixes, mapped back to §1.3:

- The port is discovered, not guessed — bug #2 cannot recur.
- `DATABASE_PATH` is set, not `DATABASE_URL` — bug #3.
- `app.getPath("appData")` on Windows is `%APPDATA%` (Roaming), matching `paths.py` exactly. Verify this: `userData` would be `%APPDATA%\EZOO POS` already and would double the folder name.
- No `startFrontend()`. Delete lines corresponding to the old `main.js:141-181`.

### 7.2 Kill the child reliably

Orphaned `ezoo-pos.exe` surviving app close is the classic bug in this architecture: the next launch finds a stale process holding the database, and the user sees a hang with no explanation.

Your existing `taskkill /T /F /PID` at `main.js:40-43` is the right approach — keep it. Add:

```js
app.on("before-quit", (e) => {
  if (backend) { e.preventDefault(); killTree(backend.pid, () => app.quit()); }
});
process.on("exit", () => backend && killTree(backend.pid));
```

Also guard against a stale process from a *previous* crash: before spawning, if a lock on the database is detected or a prior `ezoo-pos.exe` is running, either adopt it or kill it — do not spawn a second writer against the same SQLite file. Since the port is now ephemeral, two backends will both start happily and the second will fight the first over the database.

### 7.3 Window and UX

- `loadURL(\`http://127.0.0.1:${port}/\`)` after health passes.
- Show `loading.html` immediately, swap on ready. You already have `loading.html`, `error.html` and `logs.html` — keep all three; `error.html` with a "view logs" button is what saves you a support call.
- `show: false` + `ready-to-show` to avoid a white flash.
- Suppress the default menu bar in production (`Menu.setApplicationMenu(null)`), keeping a hidden devtools accelerator.
- POS-appropriate window: remember size and maximised state in a small JSON file under `userData`.
- Because printing goes through `iframe.contentWindow.print()` (`lib/utils/print-utils.ts:10-49`), verify the Electron print dialog appears and that the selected thermal/A4 printer produces correct output. Electron's print path differs from Chrome's; this needs testing on the real printer.

### 7.4 electron-builder → NSIS

```yaml
# electron/electron-builder.yml
appId: com.ezoo.pos
productName: EZOO POS
copyright: EZOO POS
directories:
  output: dist
  buildResources: build

files:
  - src/**/*
  - package.json
asar: true

extraResources:
  - from: ../backend/dist/ezoo-pos
    to: backend
    filter: ["**/*"]

win:
  target:
    - target: nsis
      arch: [x64]
  icon: build/icon.ico
  # sign: configured in Phase 5

nsis:
  oneClick: false
  perMachine: false                       # -> %LOCALAPPDATA%, no UAC prompt
  allowToChangeInstallationDirectory: true
  createDesktopShortcut: true
  createStartMenuShortcut: true
  shortcutName: EZOO POS
  deleteAppDataOnUninstall: false         # never delete the shop's data

publish:
  provider: github
  owner: <OWNER>
  repo: <REPO>
```

Two entries deserve emphasis. `perMachine: false` is what removes the admin-rights requirement. `deleteAppDataOnUninstall: false` is what prevents an uninstall from destroying the business records — the default would take `%APPDATA%\EZOO POS\` with it.

Note that `extraResources` no longer includes `../frontend/.next/standalone`. The frontend now travels inside the PyInstaller bundle as `frontend_out`.

You need `build/icon.ico` at 256×256. Without it electron-builder uses the Electron default and the app looks unfinished.

### 7.5 Auto-update

```
npm i electron-updater
```

Wire `autoUpdater.checkForUpdatesAndNotify()` a few seconds after window ready, pointed at GitHub Releases via the `publish` block above. This retires `update.bat`, which currently runs `git pull` — requiring Git on the machine and a checked-out repo, which no end user will have.

Because updates replace the install directory but not `%APPDATA%`, and because Phase 1 made `alembic upgrade head` run at startup, schema changes now apply themselves on the first launch after an update. That combination is the whole point of Phase 1.

### Acceptance criteria — Phase 4

- [ ] `npm run build:win` produces `EZOO-POS-Setup-<version>.exe`
- [ ] Installing on a **clean Windows VM** (no Python, no Node, no PostgreSQL, non-admin user) succeeds with **no UAC prompt**
- [ ] Desktop and Start Menu shortcuts launch the app
- [ ] Full workflow works: create product → make sale → print invoice → check partner wallet → export XLSX → view dashboard
- [ ] Close the app; Task Manager shows **no** surviving `ezoo-pos.exe`
- [ ] Reopen immediately: starts cleanly with data intact
- [ ] Kill `ezoo-pos.exe` while running: `error.html` appears with a usable message, not a hang
- [ ] Disconnect the network: everything still works (it is an offline app)
- [ ] Uninstall, then reinstall: previous data is still present
- [ ] Logs are written under `%APPDATA%\EZOO POS\logs\` and reachable from the UI

---

## 8. Phase 5 — CI and code signing

**Goal:** every tagged release builds itself and produces a signed installer.
**Effort:** ~0.5 day.

### 8.1 GitHub Actions

```yaml
name: build-windows
on:
  push:
    tags: ["v*"]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - uses: actions/setup-node@v4
        with: { node-version: "20" }

      - name: Build frontend (static export)
        working-directory: frontend
        run: |
          npm ci
          npm run build:export

      - name: Backend deps
        working-directory: backend
        run: |
          pip install -r requirements.txt -r requirements-dev.txt

      - name: Tests
        working-directory: backend
        run: pytest -q

      - name: PyInstaller
        working-directory: backend
        run: pyinstaller ezoo-pos.spec --clean --noconfirm

      - name: Installer
        working-directory: electron
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          npm ci
          npm run build:win

      - uses: actions/upload-artifact@v4
        with:
          name: EZOO-POS-Setup
          path: electron/dist/*.exe
```

Order matters: frontend export must precede PyInstaller, because the spec bundles `../frontend/out`. Running tests before packaging means a broken build fails in 2 minutes rather than 15.

### 8.2 Code signing

An unsigned installer shows "Windows protected your PC — unrecognised app", with the Run button hidden behind "More info". Most users stop there.

| Option | Cost | Notes |
|---|---|---|
| **Azure Trusted Signing** | ~$10/month | Cheapest legitimate route; requires a verifiable business identity; integrates with electron-builder |
| OV certificate | $200–400/year | Reputation builds over time; SmartScreen may still warn initially |
| EV certificate | $400–700/year | Immediate SmartScreen reputation; hardware token |
| Unsigned | free | Acceptable only if you personally install on the shop's machine and never distribute |

For a single-shop deployment where you do the install, unsigned is a defensible choice — decide deliberately rather than by omission. If you will send the installer to anyone else, sign it.

Store credentials as GitHub secrets; never in the repo.

### Acceptance criteria — Phase 5

- [ ] Pushing a `v*` tag produces an installer artifact with no manual steps
- [ ] The CI-built installer passes the entire Phase 4 checklist
- [ ] If signing is enabled: `signtool verify /pa` succeeds and SmartScreen shows no warning
- [ ] `electron-updater` successfully moves a test machine from `v1.0.0` to `v1.0.1`, with the database intact and migrations applied

---

## 9. Phase 6 — Deferred, but on the record

Not required for the installer. Listed because the audit found them and they should be decisions, not oversights.

### 9.1 Authentication does not exist

`frontend/app/login/page.tsx:25` is `onSubmit={(e) => e.preventDefault()}`. There is no auth endpoint, no JWT handling, no session, no password hashing, no middleware. The form ships with `admin@ezoo.pos / password123` visible in the source. `api-client.ts:37-39` redirects to `/login` on 401/403, but nothing ever returns those codes.

The three `# TODO: Add admin authorization check per FR-013` at `partners/routes.py:105,154,205` are the same gap: partner payout endpoints are unprotected.

For a single-operator offline POS on a physically controlled machine this may be acceptable. But **the login page implies protection that does not exist**, which is worse than having no login page. Either implement it or replace the page with an honest local PIN gate.

If you implement it, the minimum for this shape of app is: a local `users` table with `argon2` or `bcrypt` hashes, a login endpoint issuing a short-lived token, a FastAPI dependency on the mutating routes, and an admin role gate on the partner and settings routers. Note that binding to `127.0.0.1` (§6.1) is what keeps the current unauthenticated state from being a network-wide exposure.

### 9.2 Receipt printing could be better

Current flow generates a server-side PDF, loads it into a hidden iframe, calls `print()`, and cleans up after 5 seconds. It works, but every sale opens a print dialog and the 5-second timeout is a race.

Options if the operator complains: Electron's `webContents.print({ silent: true, deviceName })` for one-click printing to a chosen printer, or a `node-thermal-printer` ESC/POS path for direct thermal output. The latter also unlocks the cash drawer kick (`ESC p`), which is currently absent.

### 9.3 Files that should be split

Not urgent, but these will slow every future change: `export_service.py` (927 lines), `pos/service.py` (765), `reports/service.py` (613), `reports/routes.py` (562). `export_service.py` in particular is the file Phase 0 and Phase 3 both have to touch.

### 9.4 The GBP / M-PESA question

Settings say the currency is GBP; the seeded payment methods include M-PESA. Confirm which is intended before the first real sale is recorded.

---

## 10. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Arabic PDF breaks in the packaged exe | **High** | High | §6.2 `resource_path` for fonts; explicit visual check in §6.4; test before Phase 4 |
| `stamp head` on a legacy DB whose schema predates head | Medium | **Critical** | Mandatory backup; compare `PRAGMA table_info` against models before stamping |
| Existing orphan rows block FK enforcement | Medium | Medium | §4.1 `foreign_key_check` audit runs *before* the pragma is enabled |
| A missed link to an old `[id]` route | Medium | Low | Grep patterns in §5.2 + click-through of all five flows |
| Orphaned `ezoo-pos.exe` after close | Medium | High | §7.2 `before-quit` + `taskkill /T /F` + stale-process check |
| Removing pandas breaks an XLSX export path | Medium | Medium | Phase 0 acceptance criteria include a real Excel-openable file |
| PyInstaller hidden-import whack-a-mole | High | Low | Time-boxed; `console=True` while debugging; xref report |
| SmartScreen scares the user | High if unsigned | Medium | §8.2 — decide deliberately |
| Two backends writing one SQLite file | Low | **Critical** | §7.2 stale-process guard |
| CI cannot reach Google Fonts during build | Low | Medium | Fall back to `next/font/local` with the bundled Cairo TTFs |

---

## 11. Effort summary

| Phase | Work | Days | Platform |
|---|---|---|---|
| 0 | Cleanup, SQLite tests, dependency split, drop pandas | 0.5–1 | any |
| 1 | Pragmas, alembic-at-startup, `%APPDATA%`, backups | 1 | any |
| 2 | Static export, 5 route conversions, StaticFiles mount | 1 | any |
| 3 | PyInstaller on Windows, fonts, spec file | 1 | **Windows** |
| 4 | Electron rewrite, NSIS installer, auto-update | 0.5–1 | **Windows** |
| 5 | CI workflow, signing | 0.5 | any |
| | **Total** | **4.5–5.5** | |
| 6 | Auth, printing, refactors | separate decision | |

Substantially less than a from-scratch Postgres migration would have cost, because §1.1 — that work was already done.

---

## 12. Final smoke test

Run this on a **clean Windows VM** with a non-admin account, no Python, no Node, no PostgreSQL. This is the definition of done.

**Install**
1. Copy `EZOO-POS-Setup.exe` to the VM
2. Double-click. No SmartScreen block (if signed). No UAC prompt.
3. Accept defaults through the installer
4. App launches from the desktop shortcut

**Data**
5. Create a category, then a product with base and selling price
6. Assign the product to a partner with a share percentage
7. Create a supplier, record a purchase, then a partial payment
8. Create a customer with a credit limit

**Sell**
9. Make a cash sale with two line items, one fee and VAT
10. Verify subtotal / fees / VAT / grand total to the penny by hand
11. Print the invoice — **Arabic text joined and correctly ordered**
12. Check the partner wallet credited the expected amount
13. Reverse the sale; confirm stock, wallet and ledger all unwind

**Report**
14. Dashboard renders with charts
15. Export XLSX — opens in Excel, Arabic readable, numbers correct
16. Export PDF — Arabic correct
17. Customer and supplier ledgers balance

**Survive**
18. Close the app. Task Manager: no `ezoo-pos.exe`.
19. Reopen: all data present
20. Disconnect the network: everything still works
21. Kill `ezoo-pos.exe` mid-session: clean error screen, logs accessible
22. Hard-reboot the VM mid-sale: app recovers, database not corrupt
23. Confirm today's backup exists in `%APPDATA%\EZOO POS\backups\`
24. Copy that backup elsewhere, delete the live DB, restore the backup, relaunch: data returns
25. Uninstall, reinstall: data survives
26. Install `v1.0.1` over `v1.0.0`: updates in place, data intact, migrations applied

Item 22 is the one people skip. It is also the one that matters in a shop where the power goes out.
