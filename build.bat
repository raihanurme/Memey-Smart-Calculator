@echo off
setlocal
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "MemeySmartCalculator" ^
  --collect-all customtkinter ^
  main.py
if errorlevel 1 exit /b %errorlevel%
echo Build complete: dist\MemeySmartCalculator.exe
