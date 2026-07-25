const { app, BrowserWindow, Menu, ipcMain } = require("electron");
const { spawn, exec } = require("child_process");
const net = require("net");
const path = require("path");
const fs = require("fs");
const http = require("http");

const isDev = !app.isPackaged;
const STARTUP_TIMEOUT = 60_000;

let mainWindow = null;
let backend = null;
let port = null;

const userDataPath = app.getPath("userData");
const logsPath = path.join(userDataPath, "logs");
const dbDir = path.join(userDataPath);

function log(message) {
  try {
    if (!fs.existsSync(logsPath)) {
      fs.mkdirSync(logsPath, { recursive: true });
    }
    const logFile = path.join(
      logsPath,
      `ezoo-pos-${new Date().toISOString().split("T")[0]}.log`
    );
    const timestamp = new Date().toISOString();
    fs.appendFileSync(logFile, `[${timestamp}] ${message}\n`);
  } catch (_) {}
  console.log(message);
}

function findFreePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.unref();
    srv.on("error", reject);
    srv.listen(0, "127.0.0.1", () => {
      const { port: p } = srv.address();
      srv.close(() => resolve(p));
    });
  });
}

function backendExe() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "backend", "ezoo-pos.exe");
  }
  return path.join(
    __dirname,
    "..",
    "..",
    "backend",
    "dist",
    "ezoo-pos",
    "ezoo-pos.exe"
  );
}

function killTree(pid) {
  return new Promise((resolve) => {
    exec(`taskkill /T /F /PID ${pid}`, () => resolve());
  });
}

function killStaleBackend() {
  return new Promise((resolve) => {
    if (process.platform !== "win32") return resolve();
    exec(
      'tasklist /FI "IMAGENAME eq ezoo-pos.exe" /NH',
      (err, stdout) => {
        if (err) return resolve();
        const lines = stdout
          .split("\n")
          .filter((l) => l.includes("ezoo-pos.exe"));
        for (const line of lines) {
          const parts = line.trim().split(/\s+/);
          const pid = parseInt(parts[1], 10);
          if (pid && pid !== process.pid) {
            log(`Killing stale backend PID ${pid}`);
            exec(`taskkill /T /F /PID ${pid}`);
          }
        }
        resolve();
      }
    );
  });
}

function checkHealth(targetPort) {
  return new Promise((resolve) => {
    const req = http.get(
      `http://127.0.0.1:${targetPort}/health`,
      (res) => {
        resolve(res.statusCode === 200);
        res.resume();
      }
    );
    req.on("error", () => resolve(false));
    req.setTimeout(3000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function waitForHealth(targetPort) {
  const deadline = Date.now() + STARTUP_TIMEOUT;
  while (Date.now() < deadline) {
    if (await checkHealth(targetPort)) return true;
    await new Promise((r) => setTimeout(r, 500));
  }
  return false;
}

async function startBackend() {
  await killStaleBackend();

  port = await findFreePort();
  const dbPath = path.join(dbDir, "ezoo_pos.db");

  const exe = backendExe();
  log(`Starting backend: ${exe} on port ${port}`);

  backend = spawn(exe, [], {
    env: {
      ...process.env,
      EZOO_PORT: String(port),
      DATABASE_PATH: dbPath,
    },
    cwd: path.dirname(exe),
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true,
  });

  backend.stdout.on("data", (d) => log(`[api] ${d.toString().trim()}`));
  backend.stderr.on("data", (d) => log(`[api:err] ${d.toString().trim()}`));
  backend.on("exit", (code) => {
    log(`Backend exited with code ${code}`);
    backend = null;
  });

  if (!(await waitForHealth(port))) {
    throw new Error("Backend failed to start within timeout");
  }
  log("Backend is healthy");
}

function createWindow() {
  const windowState = loadWindowState();

  mainWindow = new BrowserWindow({
    width: windowState.width,
    height: windowState.height,
    x: windowState.x,
    y: windowState.y,
    show: false,
    backgroundColor: "#ffffff",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      devTools: isDev,
    },
  });

  if (windowState.maximized) mainWindow.maximize();

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });

  mainWindow.on("close", () => {
    saveWindowState(mainWindow);
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  mainWindow.loadFile(path.join(__dirname, "renderer", "loading.html"));

  mainWindow.webContents.on("did-finish-load", () => {
    if (mainWindow && mainWindow.webContents.getURL().includes("loading")) {
      mainWindow.loadURL(`http://127.0.0.1:${port}/`);
    }
  });
}

function showErrorScreen(message) {
  log(`Showing error screen: ${message}`);
  if (mainWindow) {
    mainWindow.loadFile(path.join(__dirname, "renderer", "error.html"));
    mainWindow.webContents.once("did-finish-load", () => {
      mainWindow.webContents.send("show-error", message);
    });
  }
}

function loadWindowState() {
  const defaults = { width: 1400, height: 900, maximized: false };
  try {
    const stateFile = path.join(userDataPath, "window-state.json");
    if (fs.existsSync(stateFile)) {
      return { ...defaults, ...JSON.parse(fs.readFileSync(stateFile, "utf8")) };
    }
  } catch (_) {}
  return defaults;
}

function saveWindowState(win) {
  if (!win) return;
  try {
    const isMax = win.isMaximized();
    let bounds;
    if (!isMax) bounds = win.getBounds();
    const prev = loadWindowState();
    const state = {
      width: isMax ? prev.width : bounds.width,
      height: isMax ? prev.height : bounds.height,
      x: isMax ? prev.x : bounds.x,
      y: isMax ? prev.y : bounds.y,
      maximized: isMax,
    };
    fs.writeFileSync(
      path.join(userDataPath, "window-state.json"),
      JSON.stringify(state)
    );
  } catch (_) {}
}

async function startup() {
  try {
    log("Starting EZOO POS...");
    fs.mkdirSync(dbDir, { recursive: true });
    fs.mkdirSync(logsPath, { recursive: true });

    await startBackend();
    createWindow();

    if (app.isPackaged) {
      try {
        const { autoUpdater } = require("electron-updater");
        autoUpdater.logger = { info: log, warn: log, error: log };
        autoUpdater.checkForUpdatesAndNotify().catch(() => {});
      } catch (_) {}
    }

    log("EZOO POS started successfully");
  } catch (err) {
    log(`Startup failed: ${err.message}`);
    showErrorScreen(err.message);
  }
}

app.on("ready", () => {
  const gotLock = app.requestSingleInstanceLock();
  if (!gotLock) {
    app.quit();
    return;
  }

  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  if (!isDev) {
    Menu.setApplicationMenu(null);
  }

  startup();
});

app.on("before-quit", (e) => {
  if (backend) {
    e.preventDefault();
    killTree(backend.pid).then(() => {
      backend = null;
      app.quit();
    });
  }
});

process.on("exit", () => {
  if (backend) killTree(backend.pid);
});

process.on("uncaughtException", (err) => {
  log(`Uncaught exception: ${err.message}`);
});

process.on("unhandledRejection", (err) => {
  log(`Unhandled rejection: ${err}`);
});

ipcMain.handle("get-logs", () => {
  try {
    if (!fs.existsSync(logsPath)) return "No logs yet";
    const files = fs
      .readdirSync(logsPath)
      .filter((f) => f.endsWith(".log"));
    if (files.length === 0) return "No logs yet";
    const latest = files.sort().pop();
    return fs.readFileSync(path.join(logsPath, latest), "utf8");
  } catch (err) {
    return `Error reading logs: ${err.message}`;
  }
});

ipcMain.handle("retry-startup", async () => {
  if (backend) {
    await killTree(backend.pid);
    backend = null;
  }
  setTimeout(startup, 1000);
  return "Retrying...";
});

ipcMain.handle("print-pdf", async (event, base64Data, printerName) => {
  let printWindow = null;
  try {
    printWindow = new BrowserWindow({
      show: false,
      webPreferences: { offscreen: true },
    });

    await printWindow.loadURL(
      `data:application/pdf;base64,${base64Data}`
    );

    const printResult = await new Promise((resolve) => {
      const options = {
        silent: !!printerName,
        deviceName: printerName || "",
        printBackground: true,
      };

      printWindow.webContents.print(options, (success, failureReason) => {
        if (!success) {
          log(`Print failed: ${failureReason}`);
        }
        resolve({ success, failureReason });
      });
    });

    if (printWindow) {
      printWindow.close();
      printWindow = null;
    }
    return printResult;
  } catch (err) {
    log(`Print error: ${err.message}`);
    if (printWindow) {
      printWindow.close();
    }
    return { success: false, error: err.message };
  }
});
