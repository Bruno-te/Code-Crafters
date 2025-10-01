@echo off
echo Starting MoMo SMS Transaction API Server...
echo.
echo Authentication: username=admin, password=password123
echo Server will run on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
python server.py --port 8000
pause
