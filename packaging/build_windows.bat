@echo off
REM ============================================================
REM Build the Windows distribution (single folder)
REM   pip install pyinstaller
REM   packaging\build_windows.bat
REM ============================================================
cd /d %~dp0\..
python -m PyInstaller --noconfirm --clean packaging\DrillingProgram.spec
echo.
echo Done. Output: dist\DrillingProgram\
pause
