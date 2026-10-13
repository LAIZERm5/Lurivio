@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto install
where py >nul 2>nul
if errorlevel 1 goto nopython
py -3.11 -c "import struct; assert struct.calcsize('P') == 8" >nul 2>nul
if errorlevel 1 goto nopython
py -3.11 -m venv .venv
if errorlevel 1 goto failed
:install
if exist ".venv\installed-v061.ok" goto run
 echo Installing Lurivio 0.6.1 libraries. Close any old Lurivio first.
 echo Internet is needed for installation only. Please wait.
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
 echo OK>".venv\installed-v061.ok"
:run
start "" ".venv\Scripts\pythonw.exe" "%~dp0Launch.py"
exit /b 0
:nopython
 echo Install Python 3.11, Windows 64-bit, from:
 echo https://www.python.org/downloads/release/python-3119/
 echo Choose Windows installer (64-bit). Keep Python launcher enabled.
 pause
 exit /b 1
:failed
 echo Installation failed. Check the output above, then retry Start.bat.
 pause
 exit /b 1
