@echo off
setlocal
title Stop EZOO POS Services

echo ==========================================
echo       Stop EZOO POS Services
echo ==========================================
echo.

echo [*] Stopping Backend (Python)...
:: Find process by port 8001 and kill it
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do taskkill /F /PID %%a /T 2>nul

echo [*] Stopping Frontend (Node)...
:: Find process by port 3000 and kill it
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /F /PID %%a /T 2>nul

:: Backup: kill common processes if port check failed (optional, but safer to use ports)
:: taskkill /F /IM uvicorn.exe /T 2>nul
:: taskkill /F /IM node.exe /T 2>nul

echo.
echo ==========================================
echo Services stopped!
echo ==========================================
echo.
pause
