@echo off
title Stop Ink Explainer Studio
echo =================================================================
echo   STOPPING INK EXPLAINER STUDIO BACKGROUND SERVICES
echo =================================================================
echo.

set FOUND=0
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000 " ^| findstr "LISTENING"') do (
    set FOUND=1
    echo Terminating background studio service PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

if "%FOUND%"=="1" (
    echo.
    echo [SUCCESS] Ink Explainer Studio background service has been stopped.
) else (
    echo [INFO] No active Ink Explainer Studio background service found on port 5000.
)
echo.
ping -n 4 127.0.0.1 >nul
