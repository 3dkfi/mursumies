@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 mursumies.py
  goto loppu
)
where python >nul 2>&1
if not errorlevel 1 (
  python mursumies.py
  goto loppu
)
echo Python 3 puuttuu. Asenna Python osoitteesta python.org.
:loppu
pause
