@echo off
chcp 65001 >nul
cd /d "%~dp0"

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw leetcode_whale.py
) else (
    start "" python leetcode_whale.py
)
