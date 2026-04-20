# Tasks: Electron Desktop App for EZOO POS

**Feature**: Convert EZOO POS to Offline Windows Desktop Application  
**Branch**: `007-electron-desktop-app`  
**Generated**: 2026-04-19

## Dependencies

```
Phase 1: Setup
  └─ Phase 1b: Build Preparation (frontend build, backend package)
        └─ Phase 2: Foundational (Electron main code)
              └─ Phase 3: US1 Install/Launch
                    └─ Phase 4: US2 Offline Operation
                          └─ Phase 5: US3 Stable Startup
                                └─ Phase 6: US4 Error Recovery
                                      └─ Phase 7: Polish
```

All user stories are sequential - User Story 1 is the MVP.

## Parallel Opportunities

- T007 and T008 can run in parallel (separate files)
- T015 and T016 can run in parallel (backend spawn vs frontend spawn)
- T004, T005, T006 can run in parallel (build prep steps)

## Phase 1: Setup

- [X] T001 Create electron/ directory structure with src/, renderer/ subdirectories in project root
- [X] T002 Create electron/package.json with Electron, electron-builder dependencies
- [X] T003 Create electron/electron-builder.yml for Windows build configuration

## Phase 1b: Build Preparation

- [X] T004 Configure next.config.js: output: 'standalone'
- [X] T005 Build Next.js production: npm run build (creates .next/standalone)
- [ ] T006 Package FastAPI with PyInstaller: --hidden-imports --name ezoo-pos --distpath backend/dist

## Phase 2: Foundational

- [X] T007 Create Electron main process in electron/src/main.js with port checking
- [X] T008 Create preload script in electron/src/preload.js for IPC
- [X] T009 Create loading screen in electron/src/renderer/loading.html
- [X] T010 Create error screen in electron/src/renderer/error.html with retry button
- [ ] T011 Initialize SQLite database: path.join(app.getPath('userData'), 'database.db')
- [ ] T012 Run Base.metadata.create_all() for local version (not Alembic)
- [X] T013 Add single instance lock: app.requestSingleInstanceLock() in electron/src/main.js

## Phase 3: User Story 1 - Install and Launch

- [ ] T014 Add backend /health endpoint returning 200 OK in FastAPI (if missing)
- [X] T015 [P] [US1] Spawn backend: backend/dist/ezoo-pos.exe with DATABASE_URL, host 127.0.0.1
- [X] T016 [P] [US1] Spawn frontend: node .next/standalone/server.js with PORT=3000 env
- [X] T017 [US1] Implement port conflict detection and handling (kill existing or switch ports)
- [X] T018 [US1] Implement health check: GET /health for backend ready (not just port check)
- [X] T019 [US1] Implement health check: GET / for frontend ready (wait for full response)
- [X] T020 [US1] Implement Electron window creation and loading transition
- [X] T021 [US1] Configure fullscreen/maximized window mode
- [X] T022 [US1] Use absolute paths: path.join(process.resourcesPath, ...) for bundled files

## Phase 4: User Story 2 - Offline Operation

- [X] T023 [US2] Configure database path in Electron (app.getPath('userData'))
- [X] T024 [US2] Pass DATABASE_URL to backend via environment in spawned process
- [X] T025 [US2] Set NEXT_PUBLIC_API_URL=http://localhost:8000 in frontend env before build
- [X] T026 [US2] Verify backend uses local SQLite (no external connections)

## Phase 5: User Story 3 - Stable Startup/Shutdown

- [X] T027 [US3] Implement process cleanup on app close: kill process tree in electron/src/main.js
- [X] T028 [US3] Use Windows taskkill /T /F for proper process tree termination
- [X] T029 [US3] Add startup timeout handling (max 60 seconds)

## Phase 6: User Story 4 - Error Recovery

- [X] T030 [US4] Add error screen trigger on backend spawn failure in electron/src/main.js
- [X] T031 [US4] Add detailed error logging with exact failure reason in electron/src/main.js
- [X] T032 [US4] Add error screen trigger on frontend spawn failure in electron/src/main.js
- [X] T033 [US4] Implement retry: kill all processes, restart full startup sequence in electron/src/main.js
- [ ] T034 Optional: Implement dynamic port fallback (try next port if occupied)

## Phase 7: Polish

- [X] T035 Add application logging to: app.getPath('userData')/logs/ directory
- [X] T036 Implement built-in log viewer UI in electron/src/renderer/logs.html
- [X] T037 Verify developer tools are disabled in Electron production build
- [X] T038 Configure electron-builder.yml with proper files: frontend/.next, backend/dist
- [ ] T039 Build production installer (electron-builder) in electron/
- [ ] T040 [P] Verify .exe runs on clean Windows machine

## Build Artifacts

These are bundled in the final .exe installer:
- `frontend/.next` - Next.js production build (T004)
- `backend/ezoo-pos.exe` - PyInstaller backend (T005)
- `electron/dist/` - Electron app

## Implementation Strategy

**MVP (User Story 1 only)**: Tasks T001-T022 (setup, build prep, foundational, database init, single lock, process spawning)
**Incremental Delivery**: Add User Story 2 (T023-T026), then User Story 3 (T027-T029), then User Story 4 (T030-T034)  
**Polish**: Final phase (T035-T040)

### Task Count: 40 tasks
- Phase 1: Setup (3 tasks)
- Phase 1b: Build Preparation (3 tasks)
- Phase 2: Foundational (7 tasks)
- Phase 3: US1 Install/Launch (9 tasks)
- Phase 4: US2 Offline Operation (4 tasks)
- Phase 5: US3 Stable Startup (3 tasks)
- Phase 6: US4 Error Recovery (5 tasks)
- Phase 7: Polish (6 tasks)