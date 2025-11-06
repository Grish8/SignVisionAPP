# SignVision Application Startup Script
# This script starts all three components of the SignVision app:
# 1. React Frontend (port 5173)
# 2. Node.js Backend (port 3001) 
# 3. Flask AR App (port 5000)

Write-Host "Starting SignVision Application..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient("127.0.0.1", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Check for port conflicts
Write-Host "Checking for port conflicts..." -ForegroundColor Yellow
$ports = @(3001, 5000, 5173)
$conflicts = @()

foreach ($port in $ports) {
    if (Test-Port $port) {
        $conflicts += $port
    }
}

if ($conflicts.Count -gt 0) {
    Write-Host "WARNING: The following ports are already in use: $($conflicts -join ', ')" -ForegroundColor Red
    Write-Host "Please close applications using these ports or modify the configuration." -ForegroundColor Red
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host "Startup cancelled." -ForegroundColor Red
        exit 1
    }
}

# Check if Python is available
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.8+ and add it to PATH." -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found. Please install Node.js 16+ and add it to PATH." -ForegroundColor Red
    exit 1
}

# Check if required directories exist
$requiredDirs = @("sign-in-page\frontend", "sign-in-page\server")
foreach ($dir in $requiredDirs) {
    if (!(Test-Path $dir)) {
        Write-Host "Required directory not found: $dir" -ForegroundColor Red
        exit 1
    }
}

Write-Host "All checks passed!" -ForegroundColor Green
Write-Host ""

# Install dependencies if needed
if (!(Test-Path "node_modules")) {
    Write-Host "Installing root dependencies..." -ForegroundColor Yellow
    npm install
}

if (!(Test-Path "sign-in-page\frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location "sign-in-page\frontend"
    npm install
    Set-Location "..\..\"
}

if (!(Test-Path "sign-in-page\server\node_modules")) {
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    Set-Location "sign-in-page\server"
    npm install
    Set-Location "..\..\"
}

# Start the applications
Write-Host ""
Write-Host "Starting all services..." -ForegroundColor Green
Write-Host "React Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Node.js Backend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "Flask AR App: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Cyan

# Start all services concurrently
Write-Host "" 
Write-Host "*** Browser will open automatically to: http://localhost:5173 ***" -ForegroundColor Cyan
Write-Host "*** Please login there first before using the AR application! ***" -ForegroundColor Yellow
Write-Host "" 

# Start services and open browser
try {
    # Start npm run dev in background and capture output
    npm run dev
    
} catch {
    Write-Host ""
    Write-Host "Error occurred while starting services." -ForegroundColor Red
    Write-Host "Please check the error messages above and ensure:" -ForegroundColor Yellow
    Write-Host "  1. All dependencies are installed (npm run install-all)" -ForegroundColor White
    Write-Host "  2. Python Flask dependencies are installed (pip install -r requirements.txt)" -ForegroundColor White
    Write-Host "  3. Database is set up and running (for authentication)" -ForegroundColor White
    Write-Host "  4. No other applications are using ports 3001, 5000, or 5173" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "Services stopped. Goodbye!" -ForegroundColor Green
