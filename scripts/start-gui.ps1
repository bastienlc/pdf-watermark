$port = if ($env:WATERMARK_GUI_PORT) { $env:WATERMARK_GUI_PORT } else { "7860" }
$projectRoot = Split-Path $PSScriptRoot -Parent
$pidFile = Join-Path $projectRoot ".gui.pid"

if (Test-Path $pidFile) {
    $existingPid = [int](Get-Content $pidFile -Raw).Trim()
    if (Get-Process -Id $existingPid -ErrorAction SilentlyContinue) {
        Write-Host "GUI is already running (PID $existingPid) on http://localhost:$port"
        exit 0
    }
    Remove-Item $pidFile
}

$process = Start-Process -FilePath "uv" -ArgumentList "run", "watermark-gui" `
    -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru

$process.Id | Out-File -FilePath $pidFile -Encoding utf8 -NoNewline
Write-Host "GUI started (PID $($process.Id)) — http://localhost:$port"
