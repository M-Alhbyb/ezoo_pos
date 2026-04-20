# Quickstart: Build Windows Desktop App

## Prerequisites

- Node.js 20+
- Python 3.11
- Windows 10/11

## Build Steps

### 1. Install Node dependencies

```bash
cd electron
npm install
```

### 2. Build frontend

```bash
cd frontend
npm run build
```

### 3. Configure backend for SQLite

Update database connection string in backend configuration to use SQLite.

### 4. Run Electron in development

```bash
cd electron
npm run dev
```

### 5. Build installer

```bash
cd electron
npm run build:win
```

Output: `electron/dist/ezoo-pos-setup.exe`

## Development Workflow

1. Start backend: `cd src && uvicorn app.main:app --port 8000`
2. Start frontend: `cd frontend && npm run build && next start -p 3000`
3. Run Electron: `cd electron && npm run dev`

## Troubleshooting

- Check logs in: `%APPDATA%/ezoo-pos/logs/`
- Use log viewer in app menu
- Ensure ports 8000 and 3000 are available