$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$pidFile     = Join-Path $projectRoot ".gui.pid"
[int]$port   = if ($env:WATERMARK_GUI_PORT) { [int]$env:WATERMARK_GUI_PORT } else { 7860 }

# Kill a process tree by PID; return $true if anything was killed.
function Invoke-TreeKill ([int]$Id) {
    if (-not (Get-Process -Id $Id -ErrorAction SilentlyContinue)) { return $false }
    & taskkill /T /F /PID $Id 2>$null | Out-Null
    return $true
}

# Find all PIDs listening on $port and kill their trees; return $true if anything was killed.
function Stop-ByPort ([int]$Port) {
    $pids = netstat -ano |
        Select-String "TCP\s+\S+:$Port\s+\S+\s+LISTENING\s+(\d+)" |
        ForEach-Object { [int]$_.Matches[0].Groups[1].Value } |
        Sort-Object -Unique
    if (-not $pids) { return $false }
    foreach ($p in $pids) {
        Write-Host "Killing process $p (listening on :$Port)"
        Invoke-TreeKill $p | Out-Null
    }
    return $true
}

$killed = $false

# --- Phase 1: PID file ---
if (Test-Path $pidFile) {
    $storedPid = [int](Get-Content $pidFile -Raw).Trim()
    if (Invoke-TreeKill $storedPid) {
        Write-Host "GUI stopped (PID $storedPid)"
        $killed = $true
    } else {
        Write-Host "Stale .gui.pid (PID $storedPid not running)"
    }
    Remove-Item $pidFile -ErrorAction SilentlyContinue
}

# --- Phase 2: port sweep (catches orphaned Python processes) ---
if (Stop-ByPort $port) { $killed = $true }

if (-not $killed) { Write-Host "No running GUI found on :$port" }
