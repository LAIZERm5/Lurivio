@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\installed-v061.ok" (
 echo Run Start.bat once first, then exit Lurivio from its tray menu.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -m pip install "pyinstaller>=6.11,<7"
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onedir --windowed --name Lurivio --icon docs/assets/icon.ico --version-file tools/windows_version.txt --collect-all rapidocr_onnxruntime --collect-all onnxruntime --collect-all zxingcpp app.py
if errorlevel 1 goto failed
 copy LICENSE dist\Lurivio\ >nul
 copy THIRD_PARTY_NOTICES.md dist\Lurivio\ >nul
 copy docs\USER_GUIDE_RU.md dist\Lurivio\README_RU.md >nul
".venv\Scripts\python.exe" tools\collect_licenses.py dist\Lurivio\THIRD_PARTY_LICENSES
if errorlevel 1 goto failed
 echo Done: dist\Lurivio\Lurivio.exe
 echo Keep ALL files in dist\Lurivio together.
 echo To switch Windows startup to this EXE, toggle startup off and on in the EXE.
 pause
 exit /b 0
:failed
 echo Build failed. Check the error above.
 pause
 exit /b 1
