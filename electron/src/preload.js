const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  getLogs: () => ipcRenderer.invoke('get-logs'),
  retryStartup: () => ipcRenderer.invoke('retry-startup'),
  onShowError: (callback) => {
    ipcRenderer.on('show-error', (event, message) => callback(message));
  }
});