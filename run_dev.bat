@echo off
setlocal

:: This trick re-runs the script hidden (no terminal window)
if "%~1"=="hidden" goto :payload
mshta vbscript:CreateObject("WScript.Shell").Run("cmd.exe /c ""%~f0"" hidden",0)(window.close)
exit /b

:payload
:: Get the directory where the script is located
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

:: Check prerequisites (logged to a temporary file since no terminal)
echo Starting EZOO POS... > startup_log.txt

if not exist "backend\venv\Scripts\activate" (
    echo [ERROR] Backend virtual environment not found. >> startup_log.txt
    exit /b 1
)

:: Launch Backend Hidden
powershell -Command "Start-Process cmd -ArgumentList '/c cd backend && venv\Scripts\activate && uvicorn main:app --port 8001' -WindowStyle Hidden"
echo Backend launched hidden. >> startup_log.txt

:: Launch Frontend Hidden
powershell -Command "Start-Process cmd -ArgumentList '/c cd frontend && npm run dev' -WindowStyle Hidden"
echo Frontend launched hidden. >> startup_log.txt

:: Wait for services to initialize
timeout /t 10 /nobreak >nul

:: Open browser
echo Opening browser... >> startup_log.txt
start chrome "http://localhost:3000" 2>nul || start http://localhost:3000

echo Startup sequence complete. >> startup_log.txt
exit /b
