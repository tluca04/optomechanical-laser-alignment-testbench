$ErrorActionPreference = "Stop"

$pythonInstalled = $false
try {
    $ver = python --version 2>&1
    if ($LASTEXITCODE -eq 0 -and $ver -match "Python 3") {
        $pythonInstalled = $true
        Write-Host "[OK] Found $ver" -ForegroundColor Green
    }
}
catch {
    $pythonInstalled = $false
}

if (-not $pythonInstalled) {
    Write-Host "[INFO] Installing Python 3.12 via winget..." -ForegroundColor Cyan
    winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements

    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

$HostDir = $PSScriptRoot
$RootDir = Split-Path -Parent $HostDir
$VenvDir = Join-Path $RootDir ".venv"
$ReqFile = Join-Path $HostDir "requirements.txt"

if (-not (Test-Path $VenvDir)) {
    Write-Host "[INFO] Creating isolated virtual environment (.venv)..." -ForegroundColor Cyan
    python -m venv $VenvDir
}
else {
    Write-Host "[OK] Virtual environment (.venv) already exists." -ForegroundColor Green
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

Write-Host "[INFO] Installing packages into .venv..." -ForegroundColor Cyan
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r $ReqFile

Write-Host "`n[SUCCESS] Environment ready! VS Code will automatically use .venv." -ForegroundColor Green