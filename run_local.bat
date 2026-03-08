@echo off
REM Quick start script for running the Groww Mutual Fund FAQ Assistant locally on Windows

echo.
echo ==========================================
echo Groww Mutual Fund FAQ Assistant
echo Local Setup ^& Run
echo ==========================================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r phases\phase-0-foundation\requirements.txt -q
echo [OK] Dependencies installed
echo.

REM Verify .env file
echo Verifying .env configuration...
if exist "phases\phase-0-foundation\.env" (
    echo [OK] .env file found
    echo Configuration:
    for /f "tokens=1,2 delims==" %%a in (phases\phase-0-foundation\.env) do (
        if "%%a"=="GEMINI_API_KEY_1" echo   - GEMINI_API_KEY_1: %%b
        if "%%a"=="GEMINI_API_KEY_2" echo   - GEMINI_API_KEY_2: %%b
        if "%%a"=="GEMINI_API_KEY_3" echo   - GEMINI_API_KEY_3: %%b
        if "%%a"=="GROQ_API_KEY" echo   - GROQ_API_KEY: %%b
    )
) else (
    echo [ERROR] .env file not found!
    exit /b 1
)
echo.

REM Run tests
echo Running tests...
python -m pytest testing\test_category_query_consistency.py -v --tb=short -q
if %errorlevel% equ 0 (
    echo [OK] All tests passed
) else (
    echo [ERROR] Tests failed
    exit /b 1
)
echo.

REM Start the app
echo ==========================================
echo Starting Streamlit app...
echo ==========================================
echo.
echo The app will open at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

streamlit run phases\phase-5-frontend\app.py

pause
