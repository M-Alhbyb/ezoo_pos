# Research: Electron Desktop App for EZOO POS

## Decision 1: Electron + FastAPI + Next.js Integration Pattern

**Chosen Approach**: Use Electron's child_process to spawn both backend and frontend as separate processes, with port health checks before loading the app window.

**Rationale**: 
- Matches user requirement for separate uvicorn and next start processes
- Enables proper process lifecycle management (start/stop/restart)
- Allows showing loading/error states in the renderer

**Alternatives Considered**:
- Embed backend in Electron main process (rejected - more complex, harder to debug)
- Use express to proxy requests (rejected - unnecessary indirection)

---

## Decision 2: SQLite as Local Database

**Chosen Approach**: Use SQLite with SQLAlchemy async, replacing PostgreSQL connection string.

**Rationale**:
- User recommended SQLite for simplicity
- SQLite requires no external server, perfect for offline desktop
- SQLAlchemy supports SQLite with minimal config changes

**Alternatives Considered**:
- Keep PostgreSQL locally (rejected - requires user to install/configure PostgreSQL)
- Use embedded PostgreSQL like pg_embed (rejected - more complex, higher resource usage)

**Implementation Note**: Need to verify existing SQLAlchemy models work with SQLite (especially DECIMAL types).

---

## Decision 3: Process Management in Electron

**Chosen Approach**: Node.js child_process with spawn(), port polling for health checks, and process group termination on app close.

**Rationale**:
- Native Node.js capability, no extra dependencies
- Port polling is reliable for service readiness
- Process group termination ensures clean shutdown

**Key Implementation Details**:
- Spawn backend first, wait for port 8000
- Spawn frontend second, wait for port 3000
- Kill process tree on window close
- Show error screen if any process fails to start

---

## Decision 4: Build and Packaging

**Chosen Approach**: electron-builder with nsis target for Windows .exe installer.

**Rationale**:
- User specified electron-builder
- NSIS produces standard Windows installer
- Supports bundling files and directories

**Packaging Contents**:
- Pre-built Next.js production output
- Python source code for backend
- SQLite database (created on first run)
- Electron runtime

---

## Best Practices Applied

1. **Startup sequencing**: Always start backend before frontend, verify ports before proceeding
2. **Error handling**: Show user-friendly error screens with retry, don't crash silently
3. **Process cleanup**: Kill entire process tree on app close to prevent orphans
4. **Logging**: Write logs to app data directory for troubleshooting
5. **Offline-first**: All data stored locally, no network requests required