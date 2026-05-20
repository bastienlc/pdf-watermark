@echo off
setlocal EnableDelayedExpansion

set PORT=7860
if defined WATERMARK_GUI_PORT set PORT=%WATERMARK_GUI_PORT%

pushd "%~dp0.."
set "PROJECT_ROOT=%CD%"
popd

:: Check if already running on port
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":!PORT! " ^| findstr "LISTENING"') do (
    echo GUI is already running ^(PID %%a^) on http://localhost:!PORT!
    exit /b 0
)

:: Start GUI - /D sets working directory so .gui.log is relative to project root
start "watermark-gui" /B /D "!PROJECT_ROOT!" cmd /c "uv run watermark-gui >> .gui.log 2>&1"

ping -n 3 127.0.0.1 >nul 2>&1

for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":!PORT! " ^| findstr "LISTENING"') do (
    echo GUI started ^(PID %%a^) -- http://localhost:!PORT!
    exit /b 0
)

echo ERROR: GUI failed to start. Check !PROJECT_ROOT!\.gui.log
exit /b 1
