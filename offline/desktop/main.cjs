/**
 * PERCEPTA Defence C2 — Native Desktop Application Orchestrator
 * Spawns backend perception services inside the isolated user workspace,
 * creates a dedicated native Windows desktop window, and manages graceful shutdown.
 */
const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs");
const os = require("os");
const http = require("http");
const { spawn } = require("child_process");

// Determine install and user-data directories
const isPackaged = app.isPackaged;
const installDir = isPackaged
  ? process.resourcesPath
  : path.resolve(__dirname, "..", "..");

const userDataDir = path.join(
  process.env.LOCALAPPDATA || os.homedir(),
  "PERCEPTA Defence"
);

// Ensure user-data directories exist
const logsDir = path.join(userDataDir, "logs");
fs.mkdirSync(logsDir, { recursive: true });
const logFile = path.join(logsDir, "desktop_launcher.log");

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  try {
    fs.appendFileSync(logFile, line);
  } catch (_) {}
  console.log(msg);
}

log(`=== PERCEPTA DEFENCE C2 DESKTOP INITIALIZATION ===`);
log(`Install Directory: ${installDir}`);
log(`User Data Directory: ${userDataDir}`);

let mainWindow = null;
let backendProcess = null;
const BACKEND_PORT = 8000;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;

function checkBackendHealth(retries = 30, intervalMs = 400) {
  return new Promise((resolve) => {
    let attempts = 0;
    const check = () => {
      attempts++;
      const req = http.get(`${BACKEND_URL}/api/health`, (res) => {
        if (res.statusCode === 200) {
          log(`Backend verified online (attempt ${attempts})`);
          resolve(true);
        } else if (attempts < retries) {
          setTimeout(check, intervalMs);
        } else {
          resolve(false);
        }
      });
      req.on("error", () => {
        if (attempts < retries) {
          setTimeout(check, intervalMs);
        } else {
          log(`Backend health check timed out after ${attempts} attempts`);
          resolve(false);
        }
      });
      req.setTimeout(800, () => req.abort());
    };
    check();
  });
}

function startBackend() {
  log("Initializing Perception Intelligence Engine...");

  // Candidates for python executable or compiled binary
  const venvPython = path.join(installDir, "venv", "Scripts", "python.exe");
  const sysPython = "python";

  let pythonBin = venvPython;
  if (!fs.existsSync(venvPython)) {
    pythonBin = sysPython;
  }

  const env = {
    ...process.env,
    PERCEPTA_INSTALL_DIR: installDir,
    PERCEPTA_USER_DATA_DIR: userDataDir,
    APP_ENV: "offline",
    DEMO_MODE: "true",
    PYTHONUNBUFFERED: "1",
  };

  const args = [
    "-m",
    "uvicorn",
    "backend.main:app",
    "--host",
    "127.0.0.1",
    "--port",
    String(BACKEND_PORT),
  ];

  log(`Spawning backend: ${pythonBin} ${args.join(" ")} in ${installDir}`);

  try {
    backendProcess = spawn(pythonBin, args, {
      cwd: installDir,
      env: env,
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
    });

    const backendLogStream = fs.createWriteStream(
      path.join(logsDir, "backend_service.log"),
      { flags: "a" }
    );

    if (backendProcess.stdout) {
      backendProcess.stdout.pipe(backendLogStream);
    }
    if (backendProcess.stderr) {
      backendProcess.stderr.pipe(backendLogStream);
    }

    backendProcess.on("exit", (code, signal) => {
      log(`Backend process terminated with code=${code}, signal=${signal}`);
      backendProcess = null;
    });
  } catch (err) {
    log(`Failed to spawn backend process: ${err.message}`);
  }
}

function createWindow() {
  log("Creating Native PERCEPTA Application Window...");

  mainWindow = new BrowserWindow({
    width: 1600,
    height: 950,
    minWidth: 1200,
    minHeight: 720,
    title: "PERCEPTA DEFENCE C2 — BORDER INTELLIGENCE",
    backgroundColor: "#090d14",
    autoHideMenuBar: true,
    show: false, // Show gracefully once content is rendered
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  // Load the C2 application
  mainWindow.loadURL(BACKEND_URL);

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    mainWindow.focus();
    log("Native C2 application window displayed successfully.");
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

// Window control IPC handlers
ipcMain.on("window-minimize", () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.on("window-maximize", () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) mainWindow.unmaximize();
    else mainWindow.maximize();
  }
});

ipcMain.on("window-close", () => {
  if (mainWindow) mainWindow.close();
});

ipcMain.handle("get-storage-path", () => userDataDir);

// App Lifecycle
app.whenReady().then(async () => {
  // Check if backend is already running
  const isRunning = await checkBackendHealth(2, 200);
  if (!isRunning) {
    startBackend();
    await checkBackendHealth(35, 300);
  } else {
    log("Existing backend instance detected on port 8000.");
  }

  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  log("All application windows closed.");
  app.quit();
});

app.on("before-quit", () => {
  log("PERCEPTA Desktop application quitting. Terminating local services...");
  if (backendProcess) {
    try {
      backendProcess.kill("SIGTERM");
      setTimeout(() => {
        if (backendProcess) backendProcess.kill("SIGKILL");
      }, 2000);
    } catch (_) {}
  }
});
