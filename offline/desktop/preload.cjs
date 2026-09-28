/**
 * PERCEPTA Defence Desktop — Preload Script
 * Exposes safe desktop environment capabilities to the C2 Web interface.
 */
const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("perceptaDesktop", {
  platform: process.platform,
  isDesktop: true,
  appVersion: "1.0.0",
  minimizeWindow: () => ipcRenderer.send("window-minimize"),
  maximizeWindow: () => ipcRenderer.send("window-maximize"),
  closeWindow: () => ipcRenderer.send("window-close"),
  getStoragePath: () => ipcRenderer.invoke("get-storage-path"),
});
