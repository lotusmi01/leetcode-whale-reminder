@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem 优先用 DSH 自带的 Python（已内置 Pillow），否则退回系统 python
set "BUNDLED_PY=E:\DSH\DSH Desktop\resources\office-runtime\primary-runtime\dependencies\python\python.exe"
if exist "%BUNDLED_PY%" (
    "%BUNDLED_PY%" convert_mascot.py
) else (
    python convert_mascot.py
)
