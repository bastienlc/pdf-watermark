@echo off
setlocal EnableDelayedExpansion

set PORT=7860
if defined WATERMARK_GUI_PORT set PORT=%WATERMARK_GUI_PORT%

pushd "%~dp0.."
set "PROJECT_ROOT=%CD%"
popd

set "PID_FILE=!PROJECT_ROOT!\.gui.pid"
set KILLED=0

:: Phase 1: PID file (for servers started via legacy .ps1 scripts)
if exist "!PID_FILE!" (
    set /p STORED_PID=<"!PID_FILE!"
    for /f "tokens=*" %%a in ("!STORED_PID!") do set STORED_PID=%%a
    tasklist /FI "PID eq !STORED_PID!" 2>nul | find "!STORED_PID!" >nul 2>&1
    if not errorlevel 1 (
        taskkill /T /F /PID !STORED_PID! >nul 2>&1
        echo GUI stopped ^(PID !STORED_PID!^)
        set KILLED=1
    ) else (
        echo Stale .gui.pid ^(PID !STORED_PID! not running^)
    )
    del "!PID_FILE!" >nul 2>&1
)

:: Phase 2: Port sweep (catches orphaned Python/Flask processes)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":!PORT! " ^| findstr "LISTENING"') do (
    echo Killing process %%a ^(listening on :!PORT!^)
    taskkill /T /F /PID %%a >nul 2>&1
    set KILLED=1
)

if !KILLED!==0 echo No running GUI found on :!PORT!
