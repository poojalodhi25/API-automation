@echo off
cd /d "%~dp0"
echo Starting HireFlow...
echo After you see "Uvicorn running", open: http://127.0.0.1:8000/
echo.
".venv\Scripts\python.exe" run.py
pause
