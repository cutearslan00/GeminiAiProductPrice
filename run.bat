@echo off
echo Running Gemni AI Stock Predictor Python Script...

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python first.
    pause
    exit /b
)

REM Run your Python script
streamlit run app.py

pause
