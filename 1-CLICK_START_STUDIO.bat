@echo off
title Ink Explainer Studio - Autonomous Pipeline Launcher
echo =================================================================
echo   INK EXPLAINER STUDIO - PERSISTENT BACKGROUND SERVICE LAUNCHER
echo   Multi-Niche Architecture + AI Learning Codex + Native UI
echo =================================================================
echo.
cd /d "%~dp0"

:: Check if server is already running on port 5000
netstat -ano | findstr ":5000 " | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo [STUDIO] Background service is already running on port 5000.
    goto :open_browser
)

:: Detect Python executable (prefer pythonw for silent background service)
set "PY_CMD=pythonw"
where pythonw >nul 2>&1
if %errorlevel% equ 0 goto :found_python

where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :found_python
)

if exist "C:\Python313\pythonw.exe" (
    set "PY_CMD=C:\Python313\pythonw.exe"
    goto :found_python
)

if exist "C:\Python313\python.exe" (
    set "PY_CMD=C:\Python313\python.exe"
    goto :found_python
)

echo [ERROR] Python was not found in PATH or standard installation directories.
echo Please install Python or ensure it is added to your PATH.
echo.
pause
exit /b 1

:found_python
echo [STUDIO] Starting persistent background service via %PY_CMD%...
if "%PY_CMD%"=="python" (
    start "" /min "%PY_CMD%" "2- Code\web_ui.py"
) else (
    start "" "%PY_CMD%" "2- Code\web_ui.py"
)

echo [STUDIO] Waiting for studio service to bind to port 5000...
set /a ATTEMPTS=0

:check_port
ping -n 2 127.0.0.1 >nul
set /a ATTEMPTS+=1
netstat -ano | findstr ":5000 " | findstr "LISTENING" >nul
if %errorlevel% equ 0 goto :service_ready
if %ATTEMPTS% geq 15 goto :service_timeout
goto :check_port

:service_ready
echo [STUDIO] Studio service is active and listening on port 5000.
goto :open_browser

:service_timeout
echo.
echo [WARNING] Service did not bind to port 5000 within 15 seconds.
echo [HINT] If the interface does not load, run 'launch_ui.bat' to inspect console logs.
echo.

:open_browser
:: Open UI in default web browser
echo [STUDIO] Opening studio interface at http://localhost:5000...
start http://localhost:5000

echo.
echo =================================================================
echo   STUDIO IS RUNNING AS A DETACHED BACKGROUND SERVICE
echo   * Image generation will CONTINUE even if you close this window!
echo   * Image generation will CONTINUE even if you close browser tabs!
echo   * Runs until you click Pause/Stop in UI, run STOP_STUDIO.bat,
echo     or restart your PC.
echo =================================================================
echo.
echo You can safely close this window at any time. Press any key to close now.
pause >nul
