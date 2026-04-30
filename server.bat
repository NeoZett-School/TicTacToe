@echo off
setlocal
for /f "delims=" %%i in ('where python') do set "PYTHON_PATH=%%i" & goto :found
echo Python could not be found in PATH.
exit /b 1

:found
set "PY_W=%PYTHON_PATH:.exe=w.exe%"
echo Installing requirements...
"%PYTHON_PATH%" -m pip install -r requirements.txt
echo Starting program...
start "" "%PY_W%" server.py > log.txt 2>&1

if errorlevel 1 (
    echo An error occurred while running the server.
    exit /b 1
)
exit /b 0