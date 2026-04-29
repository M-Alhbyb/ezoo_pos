@echo off
setlocal
title Update EZOO POS

echo ==========================================
echo       EZOO POS - GitHub Update
echo ==========================================
echo.

:: Get the directory where the script is located
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

:: Verify git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in your system PATH.
    echo Please install Git from https://git-scm.com/
    echo.
    pause
    exit /b 1
)

echo [*] Fetching latest changes from GitHub...
git pull https://github.com/M-Alhbyb/ezoo_pos.git main

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo SUCCESS: Project is up to date!
    echo ==========================================
) else (
    echo.
    echo [ERROR] Update failed. 
    echo This could be due to network issues or local code conflicts.
    echo If you have local changes, try committing or stashing them first.
)

echo.
pause
