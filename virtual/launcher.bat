@echo off
title Gesture Control System Launcher
color 0A

echo ===============================================
echo   GESTURE CONTROL SYSTEM LAUNCHER
echo ===============================================
echo.

REM --- Check if PLCSIM Advanced is running ---
tasklist /FI "IMAGENAME eq Siemens.Simatic.PlcSim*" 2>NUL | find /I "PlcSim" >NUL
if "%ERRORLEVEL%"=="1" (
    echo [ERROR] PLCSIM Advanced is not running
    echo         Please start PLCSIM Advanced first
    echo.
    pause
    exit /b 1
)
echo [CHECK] PLCSIM Advanced is running

REM --- Check if bridge is already running ---
tasklist /FI "IMAGENAME eq PLCSIMBridge.exe" 2>NUL | find /I /N "PLCSIMBridge.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo [CHECK] Bridge already running
) else (
    echo [START] Starting PLCSIM Bridge...
    start "PLCSIM Bridge" /MIN release\PLCSIMBridge.exe
    timeout /t 2 /nobreak >nul
    echo [CHECK] Bridge started
)

REM --- Activate Python environment ---
echo [START] Activating Python environment...
call ..\..\leap_env\Scripts\activate.bat
if ERRORLEVEL 1 (
    echo [ERROR] Failed to activate Python environment
    pause
    exit /b 1
)

REM --- Start gesture detector ---
echo [START] Starting gesture detector...
echo.
echo ===============================================
echo   System ready - perform gestures!
echo   Press Ctrl+C to stop
echo ===============================================
echo.

cd gesture_control
python gesture_detector.py

echo.
echo [STOP] Gesture detector stopped
pause
