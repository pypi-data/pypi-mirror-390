@echo off
REM ============================================================================
REM MHA Toolbox Pro - Professional Launch Script
REM ============================================================================
REM 
REM This script launches the MHA Toolbox web interface with optimal settings
REM for production deployment and multi-user access.
REM
REM Usage:
REM   launch.bat                    - Start with default settings
REM   launch.bat --port 8080        - Start on custom port
REM   launch.bat --public           - Allow external connections
REM   launch.bat --multi-user       - Enable multi-user mode with cleanup
REM
REM ============================================================================

echo.
echo ============================================================================
echo   MHA TOOLBOX PRO - Meta-Heuristic Algorithm Optimization Suite
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating one...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed
    echo.
)

REM Parse command line arguments
set PORT=8501
set ADDRESS=localhost
set MULTI_USER=0

:parse_args
if "%~1"=="" goto :start_app
if /i "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--public" (
    set ADDRESS=0.0.0.0
    shift
    goto :parse_args
)
if /i "%~1"=="--multi-user" (
    set MULTI_USER=1
    shift
    goto :parse_args
)
shift
goto :parse_args

:start_app

REM Clean up expired sessions if multi-user mode
if "%MULTI_USER%"=="1" (
    echo [INFO] Multi-user mode enabled - cleaning up expired sessions...
    python -m mha_toolbox.user_profile_optimized --cleanup
    echo.
)

echo [INFO] Starting MHA Toolbox Web Interface...
echo.
echo ============================================================================
echo   Server Configuration:
echo   - Address: %ADDRESS%
echo   - Port: %PORT%
echo   - Multi-User: %MULTI_USER%
echo ============================================================================
echo.
echo [INFO] Opening browser... Please wait...
echo.
echo [TIP] Press Ctrl+C to stop the server
echo.

REM Launch streamlit with optimal settings
streamlit run mha_web_interface.py ^
    --server.port=%PORT% ^
    --server.address=%ADDRESS% ^
    --server.headless=true ^
    --server.enableCORS=true ^
    --server.enableXsrfProtection=true ^
    --server.maxUploadSize=200 ^
    --browser.gatherUsageStats=false ^
    --theme.base=light ^
    --theme.primaryColor=#FF4B4B ^
    --theme.backgroundColor=#FFFFFF ^
    --theme.secondaryBackgroundColor=#F0F2F6

echo.
echo ============================================================================
echo   Server stopped
echo ============================================================================
echo.
pause
