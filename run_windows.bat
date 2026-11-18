@echo off
title Sports Meet 2026 - Smart Guest Greeter
cd /d "%~dp0"

echo =====================================================================
echo   SPORTS MEET 2026 - SMART GUEST GREETER ^& CROWD COUNTER
echo   Tender Heart School (Streamlit Web Dashboard)
echo =====================================================================
echo.

:: 1. Verify Python Installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not added to your system PATH!
    echo Please install Python 3.9 or newer from https://www.python.org/
    echo During installation, be sure to check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: 2. Check if packages already exist in current Python environment
python -c "import streamlit, cv2, pyttsx3, PIL" >nul 2>&1
if not errorlevel 1 (
    echo [Setup] All required packages found in current Python environment.
    goto launch
)

:: 3. Create Virtual Environment if missing
if not exist "venv\Scripts\activate.bat" (
    echo [Setup] Creating virtual environment (venv)...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create Python virtual environment.
        echo Please ensure python-venv is available.
        pause
        exit /b 1
    )
    echo [Setup] Virtual environment created successfully.
)

:: 4. Activate Virtual Environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Could not activate virtual environment.
    pause
    exit /b 1
)

:: 5. Install requirements automatically on first run
if not exist "venv\.installed" (
    echo [Setup] First-time setup detected. Installing required dependencies...
    echo (Streamlit, Ultralytics YOLO, OpenCV, Pillow, pyttsx3, numpy)
    echo.
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install required packages.
        echo Please verify your internet connection and try running again.
        pause
        exit /b 1
    )
    echo Setup completed on %date% at %time% > "venv\.installed"
    echo.
    echo [Setup] All dependencies installed successfully!
    echo.
)

:launch
:: Launch the Streamlit Web Application
echo [Sports Meet 2026] Starting Streamlit Web Dashboard...
echo Opening in your browser at http://localhost:8501
echo.
python -m streamlit run app.py --server.headless=false %*

if errorlevel 1 (
    echo.
    echo [Notice] Application closed.
    pause
)
