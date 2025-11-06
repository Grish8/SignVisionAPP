@echo off
echo.
echo ======= SignVision Application =======
echo Starting all services...
echo.
echo *** Browser will open to: http://localhost:5173 ***
echo *** This is your website - login here first! ***
echo.

REM Start the main application in background
start /B npm run dev

REM Wait 8 seconds then open browser
timeout /t 8 /nobreak > nul
start http://localhost:5173

echo.
echo Services starting... Browser should open automatically!
echo Press any key to stop all services...
pause > nul

echo.
echo Stopping services...
taskkill /f /im node.exe > nul 2>&1
taskkill /f /im python.exe > nul 2>&1
echo Goodbye!
pause