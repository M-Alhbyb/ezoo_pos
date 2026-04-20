# Implementation Plan: Convert EZOO POS to Offline Windows Desktop Application

**Branch**: `007-electron-desktop-app` | **Date**: 2026-04-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-electron-desktop-app/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Wrap the existing FastAPI backend and Next.js frontend inside an Electron desktop application for fully offline Windows operation. The desktop app will start both services locally, manage their lifecycle, and provide a native Windows experience.

### Build Artifacts Bundled

- `frontend/.next` - Next.js production build
- `backend/ezoo-pos.exe` - PyInstaller-packaged backend
- Static assets from Electron renderer

### Startup Sequence

1. Check/create database at `%APPDATA%/ezoo-pos/database.db`
2. Run migrations on first launch
3. Start backend executable → wait for port 8000
4. Start Next.js server → wait for port 3000
5. Launch Electron window
6. **If any step fails**: Show error screen with exact reason in logs

### Database Initialization

- Location: `path.join(app.getPath('userData'), 'database.db')`
- Auto-create if not exists
- Run Alembic migrations on first launch

## Technical Context

**Language/Version**: Node.js 20+, Python 3.11  
**Primary Dependencies**: Electron, electron-builder, PyInstaller, Next.js  
**Storage**: SQLite (local, via SQLAlchemy)  
**Testing**: pytest, manual testing  
**Target Platform**: Windows 10/11 (x64)  
**Project Type**: desktop-app  
**Performance Goals**: App startup <60 seconds  
**Constraints**: Fully offline, minimal code changes, stable startup/shutdown  
**Scale/Scope**: Single-user local POS system

### Windows Deployment Details

**Backend Packaging**: PyInstaller (Option A) - packages FastAPI into standalone executable
**Database Location**: `%APPDATA%/ezoo-pos/database.db` (via `app.getPath('userData')`)
**Frontend Build**: Next.js production build (`next build`) - not dev server
**Path Handling**: All paths use `path.join(app.getPath('userData'), ...)` - Windows safe
**Port Handling**: Detect conflicts, auto-kill existing processes or use fallback ports

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Financial Accuracy First | ✅ Pass | Desktop app uses same backend logic; calculations remain deterministic |
| II. Single Source of Truth | ⚠️ Violation | PostgreSQL replaced with SQLite for offline operation. Trade-off required for desktop deployment without external database |
| III. Explicit Over Implicit | ✅ Pass | Same financial logic applies |
| IV. Immutable Financial Records | ✅ Pass | No changes to backend logic |
| V. Simplicity of Use | ✅ Pass | Same UX, now offline-capable |
| VI. Data Integrity | ⚠️ Review | SQLite supports DECIMAL; verify SQLAlchemy uses appropriate types |
| VII. Backend Authority | ✅ Pass | All business logic remains in FastAPI backend |
| VIII. Input Validation | ✅ Pass | No changes to validation |
| IX. Extensibility by Design | ✅ Pass | Schema compatible with multi-user/branch support |

**Violation Justification**: SQLite is required for fully offline desktop operation without requiring users to install and configure PostgreSQL. This is the core value proposition of the feature.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/                          # Python FastAPI backend (unchanged)
├── app/
├── models/
├── services/
└── tests/

frontend/                     # Next.js frontend (unchanged)
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

electron/                     # New: Electron desktop wrapper
├── src/
│   ├── main.js              # Electron main process
│   ├── preload.js           # Preload script
│   └── renderer/            # Loading/error screens
├── package.json
└── electron-builder.yml     # Build configuration
```

**Structure Decision**: Adding new `electron/` directory to wrap existing `src/` (backend) and `frontend/` (built Next.js). Backend and frontend remain unchanged; Electron orchestrates their local execution.

**Note**: Backend SQLite connection is configured via environment variable at runtime—no code changes required to backend per spec assumptions.

## Complexity Tracking

*No violations requiring justification.*

| Aspect | Decision |
|--------|----------|
| Database | SQLite for offline operation (justified in Constitution Check) |
