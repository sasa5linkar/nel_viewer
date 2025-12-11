# Serbian NER Viewer - Windows Installation Script
# This script checks for Python and installs dependencies for the Serbian NER Viewer application

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Serbian NER Viewer - Installation Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Step 1: Check for Python installation
Write-Host "Step 1: Checking for Python installation..." -ForegroundColor Yellow

$pythonCommand = $null
$pythonVersion = $null

# Try to find Python using various common commands
$pythonCommands = @("python", "python3", "py")

foreach ($cmd in $pythonCommands) {
    if (Test-CommandExists $cmd) {
        try {
            $version = & $cmd --version 2>&1
            if ($version -match "Python (\d+\.\d+\.\d+)") {
                $pythonCommand = $cmd
                $pythonVersion = $matches[1]
                Write-Host "✓ Found Python $pythonVersion using command: $cmd" -ForegroundColor Green
                break
            }
        }
        catch {
            # Continue to next command
        }
    }
}

# If Python is not found, provide manual installation instructions
if ($null -eq $pythonCommand) {
    Write-Host ""
    Write-Host "❌ Python is not installed on this computer." -ForegroundColor Red
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Yellow
    Write-Host "PYTHON INSTALLATION INSTRUCTIONS" -ForegroundColor Yellow
    Write-Host "==================================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please install Python manually by following these steps:" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 1 - Download from Python.org (Recommended):" -ForegroundColor Cyan
    Write-Host "  1. Visit: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "  2. Download the latest Python 3.x installer for Windows" -ForegroundColor White
    Write-Host "  3. Run the installer" -ForegroundColor White
    Write-Host "  4. ⚠️  IMPORTANT: Check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host "  5. Click 'Install Now'" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 2 - Using Windows Store:" -ForegroundColor Cyan
    Write-Host "  1. Open Microsoft Store" -ForegroundColor White
    Write-Host "  2. Search for 'Python 3.11' (or latest version)" -ForegroundColor White
    Write-Host "  3. Click 'Get' or 'Install'" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 3 - Using Chocolatey (if installed):" -ForegroundColor Cyan
    Write-Host "  Run: choco install python" -ForegroundColor White
    Write-Host ""
    Write-Host "After installing Python:" -ForegroundColor Green
    Write-Host "  1. Close this PowerShell window" -ForegroundColor White
    Write-Host "  2. Open a NEW PowerShell window" -ForegroundColor White
    Write-Host "  3. Run this script again: .\install.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Yellow
    Write-Host ""
    
    # Ask if user wants to open the Python download page
    $response = Read-Host "Would you like to open the Python download page now? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Start-Process "https://www.python.org/downloads/"
        Write-Host "Opening Python download page in your browser..." -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Installation cancelled. Please install Python and try again." -ForegroundColor Red
    exit 1
}

# Step 2: Check Python version compatibility
Write-Host ""
Write-Host "Step 2: Checking Python version compatibility..." -ForegroundColor Yellow

$versionParts = $pythonVersion -split '\.'
$majorVersion = [int]$versionParts[0]
$minorVersion = [int]$versionParts[1]

if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 8)) {
    Write-Host "⚠️  Warning: Python $pythonVersion detected. Python 3.8 or higher is recommended." -ForegroundColor Yellow
    Write-Host "   The application may not work correctly with older versions." -ForegroundColor Yellow
    $response = Read-Host "Do you want to continue anyway? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Installation cancelled." -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✓ Python version $pythonVersion is compatible." -ForegroundColor Green
}

# Step 3: Check for pip
Write-Host ""
Write-Host "Step 3: Checking for pip (Python package manager)..." -ForegroundColor Yellow

try {
    $pipVersion = & $pythonCommand -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ pip is installed: $pipVersion" -ForegroundColor Green
    }
    else {
        Write-Host "❌ pip is not available." -ForegroundColor Red
        Write-Host "Please reinstall Python with pip included." -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Error checking pip: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Check if requirements.txt exists
Write-Host ""
Write-Host "Step 4: Checking for requirements.txt..." -ForegroundColor Yellow

$requirementsFile = Join-Path $PSScriptRoot "requirements.txt"
if (-not (Test-Path $requirementsFile)) {
    Write-Host "❌ requirements.txt not found in the script directory." -ForegroundColor Red
    Write-Host "   Expected location: $requirementsFile" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Found requirements.txt" -ForegroundColor Green

# Step 5: Create virtual environment (optional but recommended)
Write-Host ""
Write-Host "Step 5: Virtual Environment Setup (Optional)" -ForegroundColor Yellow
Write-Host "Creating a virtual environment is recommended to avoid package conflicts." -ForegroundColor White

$usingVirtualEnv = $false
$response = Read-Host "Would you like to create a virtual environment? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    $usingVirtualEnv = $true
    
    $venvPath = Join-Path $PSScriptRoot "venv"
    
    if (Test-Path $venvPath) {
        Write-Host "⚠️  Virtual environment already exists at: $venvPath" -ForegroundColor Yellow
        $response = Read-Host "Do you want to use the existing virtual environment? (y/n)"
        if ($response -ne "y" -and $response -ne "Y") {
            Write-Host "Please delete the existing 'venv' folder and run this script again." -ForegroundColor Yellow
            exit 1
        }
    }
    else {
        try {
            & $pythonCommand -m venv $venvPath
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Virtual environment created successfully." -ForegroundColor Green
            }
            else {
                Write-Host "❌ Failed to create virtual environment." -ForegroundColor Red
                exit 1
            }
        }
        catch {
            Write-Host "❌ Error creating virtual environment: $_" -ForegroundColor Red
            exit 1
        }
    }
    
    # Activate virtual environment
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        Write-Host "Activating virtual environment..." -ForegroundColor Cyan
        try {
            & $activateScript
            Write-Host "✓ Virtual environment activated." -ForegroundColor Green
            # Update Python command to use virtual environment
            $pythonCommand = Join-Path $venvPath "Scripts\python.exe"
        }
        catch {
            Write-Host "⚠️  Could not activate virtual environment automatically." -ForegroundColor Yellow
            Write-Host "   You may need to activate it manually using:" -ForegroundColor Yellow
            Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
        }
    }
}

# Step 6: Install dependencies
Write-Host ""
Write-Host "Step 6: Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor White
Write-Host ""

try {
    & $pythonCommand -m pip install --upgrade pip
    Write-Host ""
    & $pythonCommand -m pip install -r $requirementsFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ All dependencies installed successfully!" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "❌ Some dependencies failed to install." -ForegroundColor Red
        Write-Host "   Please check the error messages above." -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "❌ Error installing dependencies: $_" -ForegroundColor Red
    exit 1
}

# Step 7: Installation complete
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "✓ Installation Complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Add your NER HTML files to the 'examples/' folder" -ForegroundColor White
Write-Host "  2. Run the application using:" -ForegroundColor White
Write-Host "     streamlit run app.py" -ForegroundColor Yellow
Write-Host "  3. Open your browser at: http://localhost:8501" -ForegroundColor White
Write-Host ""

if ($usingVirtualEnv) {
    Write-Host "Note: You created a virtual environment. Remember to activate it" -ForegroundColor Yellow
    Write-Host "      before running the application:" -ForegroundColor Yellow
    Write-Host "      .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
}

Write-Host "For more information, see README.md" -ForegroundColor White
Write-Host ""
