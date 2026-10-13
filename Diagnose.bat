@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Run Start.bat first.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" app.py
pause
