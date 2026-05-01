@echo off
setlocal EnableDelayedExpansion

set "BEST_PATH="
set "BEST_VER=0"

for %%R in (
    "HKLM\SOFTWARE\Python\PythonCore"
    "HKCU\SOFTWARE\Python\PythonCore"
) do (
    for /f "tokens=*" %%K in ('reg query %%~R 2^>nul ^| findstr /R "\\[0-9]\.[0-9]"') do (
        set "KEY=%%K"

        rem Extract version (last part of key)
        for %%V in ("!KEY!") do set "VER=%%~nxV"

        rem Split major/minor
        for /f "tokens=1,2 delims=." %%a in ("!VER!") do (
            set /a MAJOR=%%a
            set /a MINOR=%%b
        )

        rem Normalize (3.13 → 313)
        set /a CUR_VER=!MAJOR!*100 + !MINOR!

        rem Require >= 3.13
        if !CUR_VER! GEQ 313 (
            rem Query InstallPath
            for /f "tokens=2,*" %%P in (
                'reg query "!KEY!\InstallPath" /ve 2^>nul ^| find "REG_SZ"'
            ) do (
                set "CANDIDATE=%%Qpython.exe"

                if exist "!CANDIDATE!" (
                    if !CUR_VER! GTR !BEST_VER! (
                        set "BEST_VER=!CUR_VER!"
                        set "BEST_PATH=!CANDIDATE!"
                    )
                )
            )
        )
    )
)

if not defined BEST_PATH (
    echo No Python >= 3.13 found.
    exit /b 1
)

echo Selected Python: %BEST_PATH%

set "PY_W=%BEST_PATH:.exe=w.exe%"

echo Installing requirements...
"%BEST_PATH%" -m pip install -r requirements.txt

echo Starting program...
start "" "%PY_W%" server.py

exit /b 0