# TASK: Verify the EZOO POS Windows migration was actually implemented

You are auditing a repository against a migration plan that was supposedly just completed. Your job is to determine what is **actually true of the code right now**, independent of what any previous session claimed.

## Ground rules

1. **This is read-only.** Do not fix, refactor, create, or delete anything. Do not run migrations against a real database. If you find a problem, report it and move on. Fixing is a separate task.
2. **Every verdict needs evidence.** A verdict is `PASS`, `FAIL`, `PARTIAL`, or `NOT VERIFIABLE`. Each one must be followed by either a `file:line` reference, a command and its actual output, or an explicit statement of why it cannot be checked here.
3. **Do not accept a claim as evidence.** If a commit message, comment, changelog, or previous session summary says something was done, that is a claim. Verify it in the code.
4. **Absence of a thing you expected is a FAIL, not a NOT VERIFIABLE.** Reserve `NOT VERIFIABLE` for things that genuinely require a Windows machine, a real printer, or a clean VM.
5. **Report what you find, including things not on this list.** If you notice a fifth problem while checking four, say so.
6. Assume you are being lied to by the codebase, not by malice but by drift. Shortcuts, silenced tests, and swallowed exceptions are the expected failure mode.

---

## PART A — Integrity of the work itself

Do this section first. It catches the failure modes that make the rest of the audit meaningless.

### A1. Were tests silenced instead of fixed?

```bash
git log --oneline --all | head -40
git log --diff-filter=D --name-only --pretty=format:"%h %s" -- 'backend/tests/*'
grep -rn "pytest.mark.skip\|pytest.mark.xfail\|@unittest.skip" backend/tests/ | cat
grep -rn "return  # \|pass  # \|assert True" backend/tests/ | cat
```

Report:
- Every test **file** deleted, with the commit that deleted it and the stated reason
- Every test **function** deleted or emptied (compare `git show HEAD~N:path` against current for the test files touched)
- Every `skip` / `xfail`, with its `reason=` string quoted verbatim. **A skip with no reason string is a FAIL.**
- Whether the concurrency skips match the plan's stated reason (SELECT FOR UPDATE is a no-op on SQLite) or are generic

Then: total tests before the work vs. after. If the count dropped, account for every missing test.

### A2. Were exceptions swallowed?

```bash
git diff HEAD~N --unified=3 -- backend/ | grep -n -B2 -A4 "except"
grep -rn "except Exception:\s*$\|except:\s*$\|except Exception:\s*pass\|contextlib.suppress" backend/app/ | cat
```

For each new `except` block introduced by this work: quote it and state what it hides. The plan authorises exactly **one** swallowed exception — the backup call at startup. Any other new one is a FAIL until justified.

### A3. Did the money columns get converted despite the plan saying not to?

```bash
grep -rn "Numeric(12, *2)\|Numeric(5, *2)" backend/app/ | wc -l
grep -rn "to_minor\|from_minor\|minor_units\|_cents\|_piastres\|Integer()" backend/app/models/ | cat
grep -rn "TypeDecorator" backend/app/core/ | cat
```

Expected: 27 monetary/rate columns still declared as `Numeric`. Zero integer-minor-unit helpers. If any monetary column is now `Integer`, that is a **FAIL for deviating from an explicit decision** — report which columns and how many call sites were touched.

### A4. Does the money guard test actually test anything?

Open the decimal aggregation test and quote it in full. Verify:
- It inserts a real, large row count (the plan specifies ~50,000) rather than a token handful
- It compares a SQL `func.sum()` result against a Python `Decimal` sum
- It asserts equality, not approximate equality (`pytest.approx` here is a FAIL — it defeats the purpose)
- It covers the awkward values: amounts ending `.005`, `.015`, `.995`, and the `Numeric(5,2)` rate columns

Then run it and paste the output.

### A5. Scope discipline

```bash
git diff --stat HEAD~N
```

List every file changed. Flag any file that is not accounted for by a phase in the plan. Flag any commit that spans more than one phase. Flag any file over 500 lines that was rewritten wholesale rather than edited (`export_service.py`, `pos/service.py`, `reports/service.py`, `reports/routes.py`, `electron/src/main.js`).

### A6. New debt introduced

```bash
git diff HEAD~N -- backend/ frontend/ electron/ | grep -n "^+.*\(TODO\|FIXME\|HACK\|XXX\|type: ignore\|# noqa\|eslint-disable\|@ts-ignore\|@ts-expect-error\)"
```

Quote every one with its file and line. The pre-existing baseline was 3 TODOs, all in `partners/routes.py`.

---

## PART B — Phase-by-phase verification

For each numbered item, give: verdict, evidence, and — if FAIL or PARTIAL — what specifically is wrong.

### Phase 0 — Cleanup and test net

| # | Check | How |
|---|---|---|
| 0.1 | No PostgreSQL anywhere in tests | `grep -rn "postgres\|asyncpg\|psycopg" backend/tests/` → expect empty |
| 0.2 | `conftest.py` uses temp-file SQLite | Quote the fixtures in full. Confirm a **file** path, not `:memory:` |
| 0.3 | Engine singletons are reset per test | Confirm `_async_engine` and `_async_session_local` are set to `None`. Without this, every test after the first shares one DB — check by asserting two tests see different DB paths |
| 0.4 | Suite runs with no PG process | `pytest -q` — paste the full summary line |
| 0.5 | Dead deps gone from `requirements.txt` | `grep -Ei "asyncpg\|psycopg2\|pandas\|testcontainers\|pytest" backend/requirements.txt` → expect empty |
| 0.6 | `requirements-dev.txt` exists and pins pyinstaller | quote both files in full |
| 0.7 | pandas actually removed from code | `grep -rn "import pandas\|\bpd\.\|to_excel" backend/app/` → expect empty |
| 0.8 | XLSX export uses xlsxwriter directly | show the writer construction in `export_service.py` |
| 0.9 | XLSX export still produces a valid file | run the export code path; open the result with a zip/xlsx reader; paste sheet names and a few cell values |
| 0.10 | Clean venv under 150 MB | `du -sh` the venv, or `pip install -r requirements.txt` into a temp venv and measure |
| 0.11 | Postgres vestiges deleted | confirm absent: `setup_extensions.sql`, `list_tables.py`, `clear_data.py`, `backend/dist/ezoo-pos` |
| 0.12 | `.env.example` describes SQLite | quote in full; must contain no `postgresql+asyncpg` |
| 0.13 | `.gitignore` covers build output | quote the relevant lines |
| 0.14 | ruff configured and passing | show the config; run `ruff check .` and paste output |

### Phase 1 — Database hardening

| # | Check | How |
|---|---|---|
| 1.1 | Pragma listener exists | quote it. It must be a `@event.listens_for(..., "connect")` handler, **not** a one-time execute at startup |
| 1.2 | Listener is attached to the async engine | confirm it is registered on `_async_engine.sync_engine` (or globally on `Engine`), and separately on the sync engine used for migrations. A listener defined but never attached is a FAIL |
| 1.3 | FKs actually enforced at runtime | write nothing — instead run: open a session from the app's own engine and `SELECT * FROM pragma_foreign_keys` / `pragma_journal_mode`. Paste results. Expect `1` and `wal` |
| 1.4 | FK violation is rejected | find the test that inserts a child row with a bogus parent id and asserts `IntegrityError`. Run it. If no such test exists → FAIL |
| 1.5 | Orphan audit was performed | is there a `check_orphans` script? Was its output recorded anywhere (commit body, doc, log)? If the script exists but there is no record of it being run against real data, report as PARTIAL |
| 1.6 | `create_all` no longer used in app code | `grep -rn "create_all" backend/` → should appear only in `tests/` |
| 1.7 | `alembic upgrade head` runs at startup | quote the startup handler and `run_migrations()` in full |
| 1.8 | The `stamp head` branch is conditional | it must fire only when tables exist **and** `alembic_version` does not. An unconditional stamp is a FAIL |
| 1.9 | `seed_data()` is gone | `grep -rn "seed_data\|randomblob" backend/app/` → expect empty |
| 1.10 | Fresh start reaches head | against a **temp copy** of an empty dir: start the app, then read `alembic_version` and compare to `alembic heads` |
| 1.11 | Legacy start adopts cleanly | against a **temp copy** of `ezoo_pos.db`: start, confirm stamp+upgrade, confirm row counts unchanged in `products`, `sales`, `sale_items`, `partner_wallet_transactions` |
| 1.12 | Double start does not duplicate seeds | start twice against the same temp DB; `SELECT count(*) FROM payment_methods` must be identical both times |
| 1.13 | `paths.py` exists with the four helpers | quote it. Confirm `user_data_dir`, `default_database_path`, `ensure_data_dir`, `resource_path` |
| 1.14 | DB default is the user data dir | confirm `config.py` no longer defaults to a path relative to `backend/` |
| 1.15 | Backup uses `VACUUM INTO` | `grep -rn "VACUUM INTO\|shutil.copy\|copyfile" backend/app/`. A file copy instead of `VACUUM INTO` is a FAIL — under WAL it can miss committed transactions |
| 1.16 | Backup checkpoints WAL first | confirm `wal_checkpoint` precedes the vacuum |
| 1.17 | Backup cannot block startup | confirm the call is wrapped and logs on failure |
| 1.18 | Retention works | confirm 30-file pruning; verify the sort is by date and cannot delete today's file |

### Phase 2 — Static export

| # | Check | How |
|---|---|---|
| 2.1 | `next.config.mjs` quoted in full | must set `output: 'export'`, `trailingSlash: true`, `images.unoptimized` under the export branch, and keep rewrites only for dev |
| 2.2 | Build is clean | run `NEXT_OUTPUT=export npm run build`; paste the **full** output. Any warning containing "not supported with output: export" is a FAIL |
| 2.3 | No dynamic segments remain | `find frontend/app -name '*[[]*' -o -type d -name '[[]*'` → expect empty |
| 2.4 | All five pages converted | for each of `suppliers`, `partners` detail, `partners/wallet`, `customers`, `pos/history`: give the new file path and the `useSearchParams` line |
| 2.5 | Each converted page has a Suspense boundary | quote the default export of each. Missing `Suspense` around a `useSearchParams` consumer will break prerender |
| 2.6 | Each handles a missing ID | quote the guard. Confirm the message comes from `lib/constants/arabic.ts`, not a hardcoded English string |
| 2.7 | No stale links | run all of these and paste output: <br>`git grep -nE "(href\|push\|replace)\([^)]*(suppliers\|customers\|partners\|history)/\\$\{" frontend/` <br>`git grep -nE "\`/(suppliers\|customers\|partners)/\\$\{" frontend/` <br>`git grep -n "partners/assignment\b" frontend/` |
| 2.8 | Every route emitted an html file | `find frontend/out -name index.html \| sort`; cross-check against the route list in `frontend/app/` |
| 2.9 | API base URL was **not** rewritten | `grep -rn "NEXT_PUBLIC_API_BASE\|API_BASE\s*=" frontend/lib/`; count `fetch(` sites (`git grep -c "fetch(" frontend/ \| ...`). The plan's design keeps all ~83 sites on relative `/api`. If they were rewritten to absolute URLs, report it — the work was unnecessary and adds runtime failure modes |
| 2.10 | WebSocket URL is derived | quote the new `websocket-client.ts` logic. Must fall back to `window.location`, with an env override for dev |
| 2.11 | WS client reconnects | confirm backoff/retry exists — the first connect can lose the race against backend startup |
| 2.12 | StaticFiles mount is **last** | quote `main.py` and give the line numbers of every `include_router` and of the `app.mount`. **The mount line number must be greater than all of them.** If `/` is mounted before the routers, `/api/**` is shadowed |
| 2.13 | Mount is guarded for dev | confirm the `isdir` check so `uvicorn --reload` still works without a built frontend |
| 2.14 | 404 handling | confirm unmatched non-API GETs return `out/404.html` rather than a JSON error |
| 2.15 | Served end to end | start the backend, `curl -s localhost:8001/ \| head`, `curl -s localhost:8001/api/products \| head`. Both must respond correctly |
| 2.16 | RTL and Cairo intact | confirm `<html lang="ar" dir="rtl">` survives in `out/index.html`, and that font files were self-hosted into `out/_next/static/` |

### Phase 3 — PyInstaller

| # | Check | How |
|---|---|---|
| 3.1 | Port is a parameter | quote the `__main__` block. Must read `EZOO_PORT` and bind `127.0.0.1`, **not** `0.0.0.0` |
| 3.2 | Font paths go through `resource_path` | quote the font and image directory resolution in `export_service.py`. A bare `os.path.join(base_dir, "static", ...)` is a FAIL — it breaks only when someone prints |
| 3.3 | Spec file quoted in full | check `datas` includes `app/static`, `alembic`, `alembic.ini`, `../frontend/out → frontend_out`; `hiddenimports` covers the uvicorn protocol/lifespan modules and the sqlite dialects; `excludes` covers pandas/tkinter/matplotlib/pytest/watchfiles |
| 3.4 | `--onedir`, not `--onefile` | confirm a `COLLECT(...)` block exists |
| 3.5 | `console=False` | confirm, and confirm it was not left `True` from debugging |
| 3.6 | The binary is a Windows PE | `file backend/dist/ezoo-pos/ezoo-pos.exe`. Must report `PE32+` / `MS Windows`. **If it reports ELF, nothing in Phase 3 or 4 has actually been tested** — say so prominently and mark the rest of Phase 3–4 NOT VERIFIABLE |
| 3.7 | Size sane | `du -sh` the dist dir. Expect under 120 MB. If much larger, check `build/ezoo-pos/xref-*.html` and name the culprit |
| 3.8 | Bundle contains what it should | list `dist/ezoo-pos/_internal/` and confirm the Cairo TTFs, the `alembic/versions/` files, and `frontend_out/index.html` are physically present |

### Phase 4 — Electron and installer

| # | Check | How |
|---|---|---|
| 4.1 | `main.js` quoted in full | it should be roughly half its former 362 lines |
| 4.2 | Free port is discovered | confirm a `findFreePort`-style function and that no port literal (8000, 8001, 3000) remains: `grep -n "8000\|8001\|3000" electron/src/main.js` → expect empty |
| 4.3 | `DATABASE_PATH` is passed | `grep -n "DATABASE_URL\|DATABASE_PATH" electron/src/main.js`. Setting `DATABASE_URL` is the original bug — it is ignored by the backend |
| 4.4 | The DB path matches the backend's | Electron's path and `paths.py`'s `user_data_dir()` must resolve to the **same** directory. Check for the double-naming trap: `app.getPath("userData")` is already `%APPDATA%\EZOO POS`, so joining `"EZOO POS"` onto it yields `%APPDATA%\EZOO POS\EZOO POS`. State which of `appData` / `userData` is used and what the final path is |
| 4.5 | `startFrontend` is gone | `grep -n "startFrontend\|standalone\|server.js\|node " electron/src/main.js` → expect empty |
| 4.6 | Child is killed on quit | confirm a `before-quit` handler that preempts quit until the tree is dead, plus the `taskkill /T /F` path |
| 4.7 | Stale process guard | confirm something prevents spawning a second backend against the same SQLite file after a prior crash. Absence is a FAIL — two writers on one file is the worst failure mode in this design |
| 4.8 | `electron-builder.yml` quoted in full | verify: `target: nsis` (not `dir`), `perMachine: false`, `deleteAppDataOnUninstall: false`, `extraResources` points at `../backend/dist/ezoo-pos` **and no longer at `.next/standalone`**, `win.icon` set |
| 4.9 | Icon exists | confirm `electron/build/icon.ico` is present and at least 256×256 |
| 4.10 | Auto-update wired | confirm `electron-updater` in dependencies, a `publish:` block, and a `checkForUpdatesAndNotify` call |
| 4.11 | `update.bat` retired | confirm the `git pull` script is gone or documented as dev-only |
| 4.12 | Old batch scripts | state whether `setup.bat` / `run_dev.bat` / `stop_dev.bat` still exist and whether anything still references them |

### Phase 5 — CI

| # | Check | How |
|---|---|---|
| 5.1 | Workflow quoted in full | |
| 5.2 | Runs on `windows-latest` | |
| 5.3 | **Order is correct** | frontend export must precede PyInstaller (the spec bundles `frontend/out`); tests must precede packaging. Report the actual step order |
| 5.4 | Triggered by tags | confirm `push: tags: ["v*"]` |
| 5.5 | Signing state | report whether signing is configured, unconfigured, or explicitly deferred. "Unsigned" is an acceptable answer; "silently unsigned with a `sign: false` left over from the old config" is a finding |
| 5.6 | No secrets in the repo | `git grep -nE "(certificate|CSC_LINK|password|token)\s*[:=]" -- ':!*.md'` |

---

## PART C — Cannot be verified from the code

List each of these as `NOT VERIFIABLE — requires <what>`, and say whether any evidence exists that a human already did it (a note, a log, a screenshot reference in a commit).

1. Installer runs on a clean Windows VM, non-admin, no UAC prompt
2. **Arabic invoice PDF is visually correct from inside the packaged exe** — joined letters, correct direction, not boxes or reversed. This is the highest-risk item in the whole migration
3. Receipt printing works through Electron's print path on the real printer
4. No orphaned `ezoo-pos.exe` in Task Manager after closing the app
5. App recovers from a hard power-cut mid-sale with an intact database
6. Backup → delete live DB → restore → relaunch returns the data
7. `v1.0.0` → `v1.0.1` in-place update keeps data and applies migrations
8. Offline operation with the network disconnected

---

## OUTPUT FORMAT

Start with this, filled in:

```
VERDICT SUMMARY

Commits reviewed:            <range>
Files changed:               <n>

Checks PASS:                 <n>
Checks PARTIAL:              <n>
Checks FAIL:                 <n>
Checks NOT VERIFIABLE:       <n>

Binary is a Windows PE:      yes / no / not built
Tests: total / passed / skipped / deleted:
Skips lacking a reason:      <n>
New swallowed exceptions:    <n>
Money columns still Numeric: yes / no
StaticFiles mounted last:    yes / no
Deviations from the plan:    <n>

BLOCKERS  (anything that means the app does not work)
1.
2.

DEVIATIONS  (the plan said X, the code does Y — regardless of whether Y is worse)
1.

UNVERIFIED CLAIMS  (asserted done in a commit or comment, not present in the code)
1.
```

Then Part A, then Part B by phase in the numbering above, then Part C.

Rules for the report:
- Verdict, then evidence, on every single numbered item. No item omitted.
- Paste real command output. Do not paraphrase it.
- Quote in full every file the checks ask to be quoted in full.
- Where something is worse than the plan intended but still works, say so under DEVIATIONS rather than failing it.
- **No fixes, no patches, no suggested diffs.** Findings only. If you are tempted to fix something, that is the strongest signal it belongs in BLOCKERS.
- If you cannot complete the audit, say which sections you skipped and why. Prioritise, in order: Part A, then 1.1–1.12, 2.12, 3.6, 4.3–4.7.
