$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$pidFile = Join-Path $projectRoot ".gui.pid"

if (-not (Test-Path $pidFile)) {
    Write-Host "No running GUI found (.gui.pid does not exist)"
    exit 0
}

$targetPid = [int](Get-Content $pidFile -Raw).Trim()

if (-not (Get-Process -Id $targetPid -ErrorAction SilentlyContinue)) {
    Write-Host "Process $targetPid is not running (removing stale .gui.pid)"
    Remove-Item $pidFile
    exit 0
}

& taskkill /T /F /PID $targetPid 2>$null | Out-Null
Remove-Item $pidFile
Write-Host "GUI stopped (PID $targetPid)"
