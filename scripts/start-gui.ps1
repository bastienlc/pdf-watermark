$ErrorActionPreference = 'Stop'
[int]$port = if ($env:WATERMARK_GUI_PORT) { $env:WATERMARK_GUI_PORT } else { 7860 }
$projectRoot = Split-Path $PSScriptRoot -Parent
$pidFile = Join-Path $projectRoot ".gui.pid"
$logFile = Join-Path $projectRoot ".gui.log"

if (Test-Path $pidFile) {
    $existingPid = [int](Get-Content $pidFile -Raw).Trim()
    if (Get-Process -Id $existingPid -ErrorAction SilentlyContinue) {
        Write-Host "GUI is already running (PID $existingPid) on http://localhost:$port"
        exit 0
    }
    Remove-Item $pidFile
}

# cmd.exe stays alive until the Flask child exits, so its PID reliably tracks the server lifetime
$process = Start-Process -FilePath "cmd" `
    -ArgumentList "/c", "uv run watermark-gui >> `"$logFile`" 2>&1" `
    -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru

$process.Id | Out-File -FilePath $pidFile -Encoding utf8NoBOM -NoNewline

Start-Sleep -Milliseconds 800
if ($process.HasExited) {
    Remove-Item $pidFile -ErrorAction SilentlyContinue
    throw "GUI process exited immediately (exit code $($process.ExitCode)). Check $logFile for details."
}

Write-Host "GUI started (PID $($process.Id)) — http://localhost:$port"
