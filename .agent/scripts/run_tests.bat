@echo off
echo 🧪 Running tests...

:: Set paths relative to this script (assumes .agent/scripts/run_tests.bat)
set "REPO_ROOT=%~dp0..\.."
set "PROJECT_ROOT=%REPO_ROOT%\AssetManager"
set "LOG_DIR=%REPO_ROOT%\.agent\logs"

if not exist "%PROJECT_ROOT%\.venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found at %PROJECT_ROOT%\.venv
    exit /b 1
)

cd /d "%PROJECT_ROOT%"
call .venv\Scripts\activate.bat

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo 📝 capturing output to %LOG_DIR%\tests_last_run.log
python -m pytest tests/ -v > "%LOG_DIR%\tests_last_run.log" 2>&1

if %ERRORLEVEL% EQU 0 (
    echo ✅ Tests Passed!
) else (
    echo ❌ Tests Failed. Check %LOG_DIR%\tests_last_run.log for details.
)

echo.
echo 📄 Last 20 lines of output:
echo ----------------------------------------
powershell -command "Get-Content '%LOG_DIR%\tests_last_run.log' -Tail 20"
echo ----------------------------------------
