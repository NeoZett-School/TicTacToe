@echo off
title TicTacToe Server Launcher
setlocal EnableDelayedExpansion

set "VENV_DIR=.venv"
set "PY=%VENV_DIR%\Scripts\python.exe"
set "PYW=%VENV_DIR%\Scripts\pythonw.exe"

set "BEST_PY="
set "BEST_VER=0"

for /f "delims=" %%i in ('where python 2^>nul') do (
    for /f "tokens=*" %%v in ('%%i -c "import sys; v=sys.version_info; print(v[0]*100+v[1])" 2^>nul') do (
        set "VER=%%v"
        
        if !VER! GEQ 313 (
            if !VER! GTR !BEST_VER! (
                set "BEST_VER=!VER!"
                set "BEST_PY=%%i"
            )
        )
    )
)

if not defined BEST_PY (
    echo [ERROR] No Python 3.13+ found in PATH.
    pause
    exit /b 1
)

echo Using Python: %BEST_PY% (Version: !BEST_VER!)

if not exist "%PY%" (
    echo Creating virtual environment...
    "%BEST_PY%" -m venv "%VENV_DIR%"
)

echo Installing/Updating requirements...
"%PY%" -m pip install --upgrade pip >nul
"%PY%" -m pip install -r requirements.txt

echo Starting program...
start "" "%PYW%" server.py

exit /b 0