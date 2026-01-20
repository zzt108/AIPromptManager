@echo off
echo Starting AI Prompt Manager...
if not exist .venv\Scripts\activate.bat (
    echo ❌ Virtual environment not found. Please run setup first.
    exit /b 1
)

rem $env:SEQ_URL="http://localhost:5341"
set SEQ_URL=http://localhost:5341

call .venv\Scripts\activate.bat
python src/main.py
pause
