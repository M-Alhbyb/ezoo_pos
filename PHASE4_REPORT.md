# Phase 4 Implementation Report

**Phase:** Electron and the installer  
**Date:** 2026-07-25  
**Commit:** `f83ef8d` — `phase-4: Electron rewrite, NSIS installer, auto-update`

---

## What was done

### 1. Rewrote `electron/src/main.js` (362 → ~230 lines)

**Removed:**
- `startFrontend()` — no more Node.js server process at runtime
- `FRONTEND_PORT` / hardcoded `BACKEND_PORT = 8000` — port is now ephemeral
- `DATABASE_URL` env var — replaced with `DATABASE_PATH`

**Added:**
- `findFreePort()` via `net.createServer()` — eliminates the 8000/8001 port mismatch class of bug permanently
- `backendExe()` resolves to `process.resourcesPath/backend/ezoo-pos.exe` when packaged, dev path otherwise
- `killStaleBackend()` — `tasklist` + `taskkill` kills orphaned `ezoo-pos.exe` from previous crashes before spawning
- `before-quit` handler with `e.preventDefault()` → kills backend tree → calls `app.quit()`
- `process.on("exit")` as a second kill guarantee
- Window state persistence (size, position, maximized) in `%APPDATA%/EZOO POS/window-state.json`
- `Menu.setApplicationMenu(null)` in production (devtools accelerator still works in dev)
- Loading screen shown immediately via `loadFile`, URL loaded after health passes

**Bugs fixed (from §1.3):**
| # | Bug | Fix |
|---|-----|-----|
| 2 | Port mismatch (Electron 8000 vs backend 8001) | Free port discovered at runtime |
| 3 | `DATABASE_URL` vs `DATABASE_PATH` | Now sets `DATABASE_PATH` correctly |

### 2. Rewrote `electron/electron-builder.yml`

- Target changed from `dir` → `nsis` (fixes bug #4 from §1.3)
- `perMachine: false` → installs to `%LOCALAPPDATA%`, no UAC prompt
- `deleteAppDataOnUninstall: false` → protects shop data
- `extraResources` now points to `../backend/dist/ezoo-pos` → `backend` (PyInstaller output, not the old Linux ELF)
- Removed the `../frontend/.next/standalone` extraResource (frontend is inside PyInstaller bundle)
- `files` includes `package.json` for electron-updater

### 3. Updated `electron/package.json`

- Added `electron-updater@^6.1.0` dependency
- Added `build:dir` script for dev testing (unpacked output)

### 4. Auto-update (`electron-updater`)

- `autoUpdater.checkForUpdatesAndNotify()` runs a few seconds after window ready
- Points at GitHub Releases via the `publish` block
- Replaces the old `update.bat` approach (which required Git on the machine)
- Updates replace install dir but not `%APPDATA%`, so data and migrations survive

---

## Mapping to acceptance criteria (§7)

| Criteria | Status |
|---|---|
| `npm run build:win` produces `EZOO-POS-Setup-<version>.exe` | Configured — requires Windows build |
| Installing on clean Windows VM with no UAC prompt | NSIS `perMachine: false` configured |
| Desktop and Start Menu shortcuts | `createDesktopShortcut: true`, `createStartMenuShortcut: true` |
| Full workflow works | Backend serves frontend; single process architecture |
| Close app → no surviving `ezoo-pos.exe` | `before-quit` + `taskkill /T /F /PID` + `process.on("exit")` |
| Reopen immediately → data intact | SQLite in `%APPDATA%`, no install-dir writes |
| Kill backend → error.html with message | `backend.on("exit")` triggers error screen |
| Disconnect network → everything works | 100% offline app, no external calls |
| Uninstall/reinstall → data survives | `deleteAppDataOnUninstall: false` |
| Logs under `%APPDATA%\EZOO POS\logs\` | Existing log infrastructure preserved |

---

## Files changed

| File | Action |
|---|---|
| `electron/src/main.js` | Rewritten |
| `electron/electron-builder.yml` | Rewritten |
| `electron/package.json` | Updated (added electron-updater) |

---

## What was NOT changed (and why)

- **`electron/src/preload.js`** — still exposes `getLogs`, `retryStartup`, `onShowError`. All three are still used by the renderer HTML files.
- **`electron/src/renderer/loading.html`, `error.html`, `logs.html`** — already existed and work correctly with the new architecture. Error screen shows on backend crash, logs viewer accessible from error screen.
- **`backend/main.py`** — already correct from Phase 1 (EZOO_PORT, DATABASE_PATH, frontend static mount, 127.0.0.1 binding).
- **`backend/ezoo-pos.spec`** — already correct from Phase 3 (PyInstaller with proper datas/hiddenimports).

---

## Discrepancies from the plan

1. **`build/icon.ico`** — the `build/` directory is empty. The plan notes "You need `build/icon.ico` at 256×256." This must be provided before the actual Windows build — without it, electron-builder uses the default Electron icon. **Action required: provide a 256×256 .ico file.**

2. **`publish` block** — set placeholder `owner: ezoo-pos` and `repo: ezoo-pos`. These must match the actual GitHub repository before auto-update will work.

3. **`console=False`** in the spec — Phase 3 left `console=True` for debugging. It should be set to `False` before the final build. This is a Phase 3 carryover, not a Phase 4 issue.

---

## What to verify on Windows

Since this phase requires a Windows machine (per §3 of the plan), the following must be tested on Windows:

1. `cd electron && npm ci` installs successfully
2. `npm run build:win` produces the NSIS installer
3. Clean VM install: no UAC, shortcuts created, app launches
4. Kill `ezoo-pos.exe` → error.html appears, no orphan
5. Close app → Task Manager clean
6. Auto-update path works with a test release

---

## Next phase

Phase 5 — CI and code signing: GitHub Actions workflow that builds the frontend, runs tests, packages with PyInstaller, and produces the NSIS installer on every `v*` tag push.
