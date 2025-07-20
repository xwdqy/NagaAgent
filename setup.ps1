# NagaAgent 3.0 Setup Script
# Version managed by config.py
$ErrorActionPreference = "Stop"
$pythonMinVersion = "3.8"
$venvPath = ".venv"

# Check Python version
try {
    $pythonVersion = & python --version 2>&1
    $pythonVersion = $pythonVersion -replace "Python "
    if ([version]$pythonVersion -lt [version]$pythonMinVersion) {
        Write-Error "Python $pythonMinVersion or higher required, current version: $pythonVersion"
        exit 1
    }
    Write-Host "Python version check passed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Cannot check Python version: $_"
    exit 1
}

# Set working directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Create and activate virtual environment
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venvPath
}

# Activate virtual environment
try {
    & "$venvPath/Scripts/Activate.ps1"
    Write-Host "Virtual environment activated successfully" -ForegroundColor Green
} catch {
    Write-Error "Failed to activate virtual environment: $_"
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..."
if (Test-Path "pyproject.toml") {
    Write-Host "Using uv to install dependencies..." -ForegroundColor Green
    if (Get-Command "uv" -ErrorAction SilentlyContinue) {
        uv sync
    } else {
        Write-Host "uv not found, using pip..." -ForegroundColor Yellow
        pip install -e .
    }
} elseif (Test-Path "requirements.txt") {
    Write-Host "Using requirements.txt..." -ForegroundColor Green
    pip install -r requirements.txt
} else {
    Write-Host "No dependency file found, please check project configuration" -ForegroundColor Red
    exit 1
}

# Install additional requirements files if they exist
Get-ChildItem -Filter "requirements*.txt" -ErrorAction SilentlyContinue | ForEach-Object {
    pip install -r $_.FullName -i https://pypi.tuna.tsinghua.edu.cn/simple
}

# Install playwright browser drivers
Write-Host "Installing playwright browser drivers..."
python -m playwright install msedge

# Verify playwright installation
Write-Host "Verifying playwright installation..."
try {
    $playwrightVersion = python -m playwright --version
    Write-Host "Playwright version: $playwrightVersion" -ForegroundColor Green
} catch {
    Write-Error "Playwright installation verification failed: $_"
    exit 1
}

Write-Host "Environment setup completed!"
Write-Host "To install other browser drivers, run:"
Write-Host "python -m playwright install firefox  # Install Firefox"
Write-Host "python -m playwright install webkit   # Install WebKit" 