@echo off
echo Starting AI Prompt Manager (Studio Mode)...
rem $env:SEQ_URL="http://localhost:5341"
set SEQ_URL=http://localhost:5341
.venv\Scripts\python.exe src\main.py --data-dir c:\git\aiprompts %*
