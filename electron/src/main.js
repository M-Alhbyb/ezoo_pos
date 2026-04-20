const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const http = require('http');

const isDev = !app.isPackaged;

const BACKEND_PORT = 8000;
const FRONTEND_PORT = 3000;
const STARTUP_TIMEOUT = 60000;

let mainWindow = null;
let backendProcess = null;
let frontendProcess = null;

const userDataPath = app.getPath('userData');
const logsPath = path.join(userDataPath, 'logs');
const dbPath = path.join(userDataPath, 'database.db');

function log(message) {
  if (!fs.existsSync(logsPath)) {
    fs.mkdirSync(logsPath, { recursive: true });
  }
  const logFile = path.join(logsPath, `ezoo-pos-${new Date().toISOString().split('T')[0]}.log`);
  const timestamp = new Date().toISOString();
  fs.appendFileSync(logFile, `[${timestamp}] ${message}\n`);
  console.log(`[${timestamp}] ${message}`);
}

function getResourcePath(relativePath) {
  if (isDev) {
    return path.join(__dirname, '..', '..', relativePath);
  }
  return path.join(process.resourcesPath, relativePath);
}

function killProcessTree(pid) {
  return new Promise((resolve) => {
    exec(`taskkill /T /F /PID ${pid}`, (error) => {
      if (error) {
        log(`Process termination warning: ${error.message}`);
      }
      resolve();
    });
  });
}

function checkPort(port) {
  return new Promise((resolve) => {
    const req = http.get(`http://127.0.0.1:${port}`, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(1000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

function checkHealth(url, expectedStatus = 200) {
  return new Promise((resolve) => {
    const req = http.get(url, (res) => {
      resolve(res.statusCode === expectedStatus);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(5000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function waitForBackend() {
  const startTime = Date.now();
  while (Date.now() - startTime < STARTUP_TIMEOUT) {
    const healthy = await checkHealth(`http://127.0.0.1:${BACKEND_PORT}/health`);
    if (healthy) {
      log('Backend is ready');
      return true;
    }
    await new Promise((r) => setTimeout(r, 1000));
  }
  return false;
}

async function waitForFrontend() {
  const startTime = Date.now();
  while (Date.now() - startTime < STARTUP_TIMEOUT) {
    const healthy = await checkHealth(`http://127.0.0.1:${FRONTEND_PORT}/`);
    if (healthy) {
      log('Frontend is ready');
      return true;
    }
    await new Promise((r) => setTimeout(r, 1000));
  }
  return false;
}

async function startBackend() {
  return new Promise(async (resolve, reject) => {
    try {
      const backendExe = getResourcePath('backend/dist/ezoo-pos.exe');
      log(`Starting backend: ${backendExe}`);

      const dbDir = path.dirname(dbPath);
      if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
      }

      const env = { ...process.env, DATABASE_URL: `sqlite:///${dbPath}` };

      backendProcess = spawn(backendExe, [], {
        env,
        cwd: path.dirname(backendExe),
        detached: false,
        stdio: 'pipe'
      });

      backendProcess.stdout.on('data', (data) => log(`Backend: ${data}`));
      backendProcess.stderr.on('data', (data) => log(`Backend error: ${data}`));

      backendProcess.on('error', (err) => {
        log(`Backend spawn error: ${err.message}`);
        reject(err);
      });

      const ready = await waitForBackend();
      if (ready) {
        resolve();
      } else {
        reject(new Error('Backend failed to start within timeout'));
      }
    } catch (err) {
      reject(err);
    }
  });
}

async function startFrontend() {
  return new Promise(async (resolve, reject) => {
    try {
      const frontendDir = getResourcePath('frontend/.next/standalone');
      const serverJs = path.join(frontendDir, 'server.js');

      if (!fs.existsSync(serverJs)) {
        reject(new Error(`Frontend not found: ${serverJs}`));
        return;
      }

      log(`Starting frontend: ${serverJs}`);

      const env = { ...process.env, PORT: FRONTEND_PORT.toString() };

      frontendProcess = spawn('node', [serverJs], {
        env,
        cwd: frontendDir,
        detached: false,
        stdio: 'pipe'
      });

      frontendProcess.stdout.on('data', (data) => log(`Frontend: ${data}`));
      frontendProcess.stderr.on('data', (data) => log(`Frontend error: ${data}`));

      frontendProcess.on('error', (err) => {
        log(`Frontend spawn error: ${err.message}`);
        reject(err);
      });

      const ready = await waitForFrontend();
      if (ready) {
        resolve();
      } else {
        reject(new Error('Frontend failed to start within timeout'));
      }
    } catch (err) {
      reject(err);
    }
  });
}

async function cleanupProcesses() {
  log('Cleaning up processes...');

  if (frontendProcess && !frontendProcess.killed) {
    try {
      await killProcessTree(frontendProcess.pid);
    } catch (e) {}
  }

  if (backendProcess && !backendProcess.killed) {
    try {
      await killProcessTree(backendProcess.pid);
    } catch (e) {}
  }

  log('Cleanup complete');
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      devTools: isDev
    },
    show: false,
    backgroundColor: '#ffffff'
  });

  const menuTemplate = [
    {
      label: 'View',
      submenu: [
        {
          label: 'Logs',
          click: () => {
            const logsWindow = new BrowserWindow({
              width: 900,
              height: 600,
              parent: mainWindow,
              modal: false,
              webPreferences: {
                preload: path.join(__dirname, 'preload.js'),
                contextIsolation: true,
                nodeIntegration: false
              }
            });
            logsWindow.loadFile(path.join(__dirname, 'renderer', 'logs.html'));
          }
        },
        { type: 'separator' },
        { role: 'toggleDevTools' },
        { role: 'reload' }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (app.isPackaged) {
      mainWindow.maximize();
    }
  });

  mainWindow.on('closed', async () => {
    await cleanupProcesses();
    mainWindow = null;
  });

  if (process.argv.includes('--loading')) {
    mainWindow.loadFile(path.join(__dirname, 'renderer', 'loading.html'));
  } else {
    mainWindow.loadURL(`http://127.0.0.1:${FRONTEND_PORT}`);
  }
}

function showErrorScreen(message) {
  if (mainWindow) {
    mainWindow.webContents.send('show-error', message);
  }
}

async function startup() {
  try {
    log('Starting EZOO POS...');

    if (!fs.existsSync(userDataPath)) {
      fs.mkdirSync(userDataPath, { recursive: true });
    }

    try {
      await startBackend();
    } catch (backendErr) {
      log(`Backend failed: ${backendErr.message}`);
      showErrorScreen(`Backend failed to start: ${backendErr.message}`);
      return;
    }

    try {
      await startFrontend();
    } catch (frontendErr) {
      log(`Frontend failed: ${frontendErr.message}`);
      showErrorScreen(`Frontend failed to start: ${frontendErr.message}`);
      return;
    }

    createWindow();
    log('EZOO POS started successfully');
  } catch (err) {
    log(`Startup failed: ${err.message}`);
    showErrorScreen(err.message);
  }
}

app.on('ready', () => {
  const gotTheLock = app.requestSingleInstanceLock();

  if (!gotTheLock) {
    log('Another instance is already running');
    app.quit();
    return;
  }

  app.on('second-instance', async () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  startup();
});

app.on('window-all-closed', async () => {
  await cleanupProcesses();
  app.quit();
});

app.on('before-quit', async () => {
  await cleanupProcesses();
});

process.on('uncaughtException', async (err) => {
  log(`Uncaught exception: ${err.message}`);
  await cleanupProcesses();
  app.quit();
});

process.on('unhandledRejection', async (err) => {
  log(`Unhandled rejection: ${err}`);
});

ipcMain.handle('get-logs', async () => {
  try {
    const logDir = logsPath;
    if (!fs.existsSync(logDir)) {
      return 'No logs yet';
    }
    const files = fs.readdirSync(logDir).filter(f => f.endsWith('.log'));
    if (files.length === 0) {
      return 'No logs yet';
    }
    const latest = files.sort().pop();
    return fs.readFileSync(path.join(logDir, latest), 'utf8');
  } catch (err) {
    return `Error reading logs: ${err.message}`;
  }
});

ipcMain.handle('retry-startup', async () => {
  await cleanupProcesses();
  setTimeout(startup, 1000);
  return 'Retrying...';
});