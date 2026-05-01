@echo off
title TicTacToe Client Launcher
setlocal EnableDelayedExpansion

set "BEST_PATH="
set "BEST_VER=0"

rem -------------------------
rem Function: Evaluate candidate
rem -------------------------
:check_candidate
set "CAND=%~1"

if not exist "%CAND%" goto :eof

rem Extract version from path (best-effort)
for %%F in ("%CAND%") do set "NAME=%%~dpF"

rem Try to detect version like Python313, Python311, etc.
echo %CAND% | findstr /R "Python[0-9][0-9][0-9]" >nul
if not errorlevel 1 (
    for /f "tokens=2 delims=Python" %%a in ("%CAND%") do (
        set "TMP=%%a"
        set "VER=!TMP:~0,3!"
        set /a CUR_VER=!VER!
    )
) else (
    goto :eof
)

if !CUR_VER! GEQ 313 (
    if !CUR_VER! GTR !BEST_VER! (
        set "BEST_VER=!CUR_VER!"
        set "BEST_PATH=%CAND%"
    )
)

goto :eof

rem -------------------------
rem 1. Registry scan
rem -------------------------
for %%R in (
    "HKLM\SOFTWARE\Python\PythonCore"
    "HKCU\SOFTWARE\Python\PythonCore"
) do (
    for /f "tokens=*" %%K in ('reg query %%~R 2^>nul') do (
        for /f "tokens=2,*" %%P in (
            'reg query "%%K\InstallPath" /ve 2^>nul ^| find "REG_SZ"'
        ) do (
            call :check_candidate "%%Qpython.exe"
        )
    )
)

rem -------------------------
rem 2. py launcher (if exists)
rem -------------------------
where py >nul 2>nul
if not errorlevel 1 (
    for /f "tokens=2" %%i in ('py -0p 2^>nul') do (
        call :check_candidate "%%i"
    )
)

rem -------------------------
rem 3. PATH lookup
rem -------------------------
for /f "delims=" %%i in ('where python 2^>nul') do (
    call :check_candidate "%%i"
)

rem -------------------------
rem 4. Common directories
rem -------------------------
for %%D in (
    "%ProgramFiles%\Python*"
    "%ProgramFiles(x86)%\Python*"
    "%LocalAppData%\Programs\Python\Python*"
) do (
    if exist "%%~D\python.exe" (
        call :check_candidate "%%~D\python.exe"
    )
)

rem -------------------------
rem Result
rem -------------------------
if not defined BEST_PATH (
    echo No Python >= 3.13 found
    exit /b 1
)

echo Using Python: %BEST_PATH%

set "PY_W=%BEST_PATH:.exe=w.exe%"

"%BEST_PATH%" -m pip install -r requirements.txt

start "" "%PY_W%" client.py

exit /b 0