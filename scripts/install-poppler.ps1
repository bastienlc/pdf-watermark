$ErrorActionPreference = 'Stop'

# Variables
$popplerUrl = 'https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip'
$installRoot = 'C:\tools\poppler'
$zipPath = Join-Path $env:TEMP 'poppler.zip'

# Create install root
if (!(Test-Path $installRoot)) {
    New-Item -ItemType Directory -Path $installRoot | Out-Null
}

# Download Poppler
Write-Host "Downloading Poppler..."
Invoke-WebRequest -Uri $popplerUrl -OutFile $zipPath

# Extract to install root
Write-Host "Extracting Poppler..."
Expand-Archive -LiteralPath $zipPath -DestinationPath $installRoot -Force

# Find the extracted top-level poppler-* folder
$popplerTop = Get-ChildItem $installRoot -Directory | Where-Object { $_.Name -like "poppler-*" } | Select-Object -First 1
if (-not $popplerTop) {
    throw "Could not find extracted poppler-* folder in $installRoot"
}

$popplerBin = Join-Path $popplerTop.FullName 'Library\bin'
if (-Not (Test-Path $popplerBin)) {
    Throw "Could not find Poppler's 'bin' directory at $popplerBin"
}

# Add to system PATH (if not already)
$existingPath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
if ($existingPath -notlike "*$popplerBin*") {
    Write-Host "Adding $popplerBin to system PATH..."
    [Environment]::SetEnvironmentVariable('Path', "$existingPath;$popplerBin", 'Machine')
} else {
    Write-Host "'$popplerBin' is already in PATH."
}

# Cleanup
Remove-Item $zipPath -Force

# Verify installation
Write-Host "Verifying Poppler install..."
& "$popplerBin\pdftoppm.exe" -h

# Make Poppler available in PATH for current GitHub Actions job
"$popplerBin" | Out-File -FilePath $env:GITHUB_PATH -Encoding utf8 -Append

Write-Host "✅ Poppler installed successfully!"
