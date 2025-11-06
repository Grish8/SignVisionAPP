# SignVision Application Startup Script with Guaranteed Browser Opening
# This script ensures the browser opens to the website first

Write-Host "Starting SignVision Application..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

# Kill any existing processes on our ports
Write-Host "Cleaning up any existing processes..." -ForegroundColor Yellow

$portsToCheck = @(3001, 5000, 5173)
foreach ($port in $portsToCheck) {
    try {
        $processes = netstat -ano | findstr ":$port"
        if ($processes) {
            Write-Host "Found processes on port $port, cleaning up..." -ForegroundColor Yellow
            # Extract PIDs and kill them
            $processes | ForEach-Object {
                if ($_ -match '\s+(\d+)\s*$') {
                    $pid = $matches[1]
                    try {
                        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    } catch {
                        # Ignore errors
                    }
                }
            }
        }
    } catch {
        # Ignore errors during cleanup
    }
}

Write-Host ""
Write-Host "*** Browser will open automatically to: http://localhost:5173 ***" -ForegroundColor Cyan
Write-Host "*** This is your SignVision website - login here first! ***" -ForegroundColor Yellow
Write-Host ""

# Start the application
Write-Host "Starting all services..." -ForegroundColor Green

try {
    # Start npm run dev and immediately schedule browser opening
    Start-Process -FilePath "powershell" -ArgumentList "-Command", "Start-Sleep -Seconds 8; Start-Process 'http://localhost:5173'" -WindowStyle Hidden
    
    # Now start the main application
    npm run dev
    
} catch {
    Write-Host ""
    Write-Host "Error occurred while starting services." -ForegroundColor Red
    Write-Host "Please ensure:" -ForegroundColor Yellow
    Write-Host "  1. All dependencies are installed (npm run setup)" -ForegroundColor White
    Write-Host "  2. Python Flask dependencies are installed (pip install -r requirements.txt)" -ForegroundColor White
    Write-Host "  3. Database is set up and running" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "Services stopped. Goodbye!" -ForegroundColor Green