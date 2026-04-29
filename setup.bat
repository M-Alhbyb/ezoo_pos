@echo off
setlocal enabledelayedexpansion
title EZOO POS - First Time Setup

echo ==========================================
echo       EZOO POS - First Time Setup
echo ==========================================
echo.

:: Get the directory where the script is located
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

:: Check for Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Git is not installed. You might not be able to update easily.
)

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found. Attempting to install via winget...
    winget --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo [*] Installing Python 3.11...
        winget install --id Python.Python.3.11 --exact --silent --accept-package-agreements --accept-source-agreements
        if !errorlevel! equ 0 (
            echo [SUCCESS] Python installation triggered. 
            echo [!] IMPORTANT: You MUST restart this terminal window after installation finishes.
            pause
            exit /b 0
        )
    )
    echo [ERROR] Python is not installed. Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

:: Check for Node.js/NPM
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Node.js not found. Attempting to install via winget...
    winget --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo [*] Installing Node.js...
        winget install --id OpenJS.NodeJS --exact --silent --accept-package-agreements --accept-source-agreements
        if !errorlevel! equ 0 (
            echo [SUCCESS] Node.js installation triggered.
            echo [!] IMPORTANT: You MUST restart this terminal window after installation finishes.
            pause
            exit /b 0
        )
    )
    echo [ERROR] Node.js is not installed. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo [*] Setting up Backend...
echo ------------------------------------------
cd /d "%BASE_DIR%\backend"

:: Create virtual environment if it doesn't exist
:: We use venv as requested
if not exist "venv" (
    echo [*] Creating virtual environment (venv)...
    python -m venv venv
)

:: Activate virtual environment and install dependencies
echo [*] Installing backend dependencies...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

python -m pip install --upgrade pip
pip install -r requirements.txt

:: Copy .env file if it doesn't exist
if not exist ".env" (
    echo [*] Creating .env file from .env.example...
    copy .env.example .env
    echo [!] IMPORTANT: Please edit backend/.env with your database credentials.
) else (
    echo [!] backend/.env already exists, skipping copy.
)

echo.
echo [*] Setting up Frontend...
echo ------------------------------------------
cd /d "%BASE_DIR%\frontend"

:: Install frontend dependencies
echo [*] Installing frontend dependencies (npm install)...
call npm install

echo.
echo ==========================================
echo       SETUP COMPLETE!
echo ==========================================
echo.
echo Next steps:
echo 1. Configure your PostgreSQL database.
echo 2. Edit backend/.env with your DB credentials.
echo 3. Run migrations: cd backend ^&^& venv\Scripts\activate ^&^& alembic upgrade head
echo 4. Start the app: run_dev.bat
echo.
echo.
pause
