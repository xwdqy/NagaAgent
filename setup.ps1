# NagaAgent 3.0 Setup Script
# Version managed by config.py
$ErrorActionPreference = "Stop"
$pythonMinVersion = "3.10"
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
    Write-Host "Creating virtual environment..." -ForegroundColor Green
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

# Upgrade pip first
Write-Host "Upgrading pip..." -ForegroundColor Green
python.exe -m pip install --upgrade pip

# Install core dependencies first (those that need compilation)
Write-Host "Installing core dependencies (numpy, pandas, scipy)..." -ForegroundColor Green
try {
    pip install --only-binary=all numpy pandas scipy
    Write-Host "Core dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Warning: Failed to install core dependencies with --only-binary, trying without..." -ForegroundColor Yellow
    try {
        pip install numpy pandas scipy
        Write-Host "Core dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "Error: Failed to install core dependencies. Please install Visual C++ Build Tools first." -ForegroundColor Red
        Write-Host "Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Red
        exit 1
    }
}

# Install basic dependencies
Write-Host "Installing basic dependencies..." -ForegroundColor Green
$basicDeps = @(
    "mcp", "openai", "openai-agents", "python-dotenv", "requests", "aiohttp", 
    "pytz", "colorama", "python-dateutil"
)
foreach ($dep in $basicDeps) {
    try {
        pip install $dep
        Write-Host "Installed $dep" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install GRAG knowledge graph dependencies
Write-Host "Installing GRAG knowledge graph dependencies..." -ForegroundColor Green
$gragDeps = @("py2neo", "pyvis", "matplotlib")
foreach ($dep in $gragDeps) {
    try {
        pip install $dep
        Write-Host "Installed $dep" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install API server dependencies
Write-Host "Installing API server dependencies..." -ForegroundColor Green
$apiDeps = @("flask-cors", "flask", "gevent", "edge-tts", "emoji", "fastapi")
foreach ($dep in $apiDeps) {
    try {
        pip install $dep
        Write-Host "Installed $dep" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install network communication dependencies
Write-Host "Installing network communication dependencies..." -ForegroundColor Green
$networkDeps = @("uvicorn", "librosa", "websockets")
foreach ($dep in $networkDeps) {
    try {
        pip install $dep
        Write-Host "Installed $dep" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install AI/ML dependencies
Write-Host "Installing AI/ML dependencies..." -ForegroundColor Green
$aiDeps = @("tqdm", "scikit-learn", "transformers")
foreach ($dep in $aiDeps) {
    try {
        pip install $dep
        Write-Host "Installed $dep" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install data processing dependencies
Write-Host "Installing data processing dependencies..." -ForegroundColor Green
$dataDeps = @("pydantic", "pydantic-settings", "griffe", "anyio", "httpx", "httpx-sse", 
              "sse-starlette", "starlette", "certifi", "charset-normalizer", "idna", 
              "urllib3", "typing-extensions", "markdown")
foreach ($dep in $dataDeps) {
    try {
        pip install $dep
        Write-Host "Installed $dep" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install GUI dependencies
Write-Host "Installing GUI dependencies..." -ForegroundColor Green
$guiDeps = @("playwright", "greenlet", "pyee", "pygame", "html2text")
foreach ($dep in $guiDeps) {
    try {
        pip install $dep
        Write-Host "Installed $dep" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install audio processing dependencies
Write-Host "Installing audio processing dependencies..." -ForegroundColor Green
$audioDeps = @("sounddevice", "soundfile", "pyaudio", "edge-tts", "emoji")
foreach ($dep in $audioDeps) {
    try {
        pip install $dep
        Write-Host "Installed $dep" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install PyQt5
Write-Host "Installing PyQt5..." -ForegroundColor Green
try {
    pip install pyqt5
    Write-Host "PyQt5 installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Warning: Failed to install PyQt5" -ForegroundColor Yellow
}

# Install system tray dependencies
Write-Host "Installing system tray dependencies..." -ForegroundColor Green
$trayDeps = @("pystray", "pillow")
foreach ($dep in $trayDeps) {
    try {
        pip install $dep
        Write-Host "Installed $dep" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install other tool dependencies
Write-Host "Installing other tool dependencies..." -ForegroundColor Green
$toolDeps = @("tiktoken", "bottleneck")
foreach ($dep in $toolDeps) {
    try {
        pip install $dep
        Write-Host "Installed $dep" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install system control dependencies
Write-Host "Installing system control dependencies..." -ForegroundColor Green
$sysDeps = @("screen-brightness-control", "pycaw", "comtypes")
foreach ($dep in $sysDeps) {
    try {
        pip install $dep
        Write-Host "Installed $dep" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

# Install playwright browser drivers
Write-Host "Installing playwright browser drivers..." -ForegroundColor Green
try {
    python -m playwright install chromium
    Write-Host "Playwright Chromium installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Warning: Failed to install Playwright browser drivers" -ForegroundColor Yellow
}

# Verify critical dependencies
Write-Host "Verifying critical dependencies..." -ForegroundColor Green
$criticalDeps = @("numpy", "pandas", "pyqt5", "pystray", "pillow")
foreach ($dep in $criticalDeps) {
    try {
        python -c "import $dep; print('$dep - OK')"
        Write-Host "$dep verification passed" -ForegroundColor Green
    } catch {
        Write-Host "Warning: $dep verification failed" -ForegroundColor Yellow
    }
}

# Verify playwright installation
Write-Host "Verifying playwright installation..." -ForegroundColor Green
try {
    $playwrightVersion = python -m playwright --version
    Write-Host "Playwright version: $playwrightVersion" -ForegroundColor Green
} catch {
    Write-Host "Warning: Playwright installation verification failed" -ForegroundColor Yellow
}

# Test tray functionality
Write-Host "Testing tray functionality..." -ForegroundColor Green
try {
    python -c "import pystray, PIL; print('Tray dependencies - OK')"
    Write-Host "Tray functionality test passed" -ForegroundColor Green
} catch {
    Write-Host "Warning: Tray functionality test failed" -ForegroundColor Yellow
}

Write-Host "`nEnvironment setup completed!" -ForegroundColor Green
Write-Host "To install other browser drivers, run:" -ForegroundColor Cyan
Write-Host "python -m playwright install firefox  # Install Firefox" -ForegroundColor Cyan
Write-Host "python -m playwright install webkit   # Install WebKit" -ForegroundColor Cyan
Write-Host "`nTo start with tray mode, run:" -ForegroundColor Cyan
Write-Host ".\start_with_tray.bat" -ForegroundColor Cyan 
