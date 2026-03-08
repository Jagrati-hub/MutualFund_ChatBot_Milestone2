@echo off
echo Stopping any Python processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo Deleting Chroma database...
cd /d "%~dp0phases\phase-2-processing"
if exist chroma (
    rmdir /s /q chroma
    echo Chroma deleted!
) else (
    echo Chroma directory not found.
)

echo.
echo Done! Now run the scraper and ingestor:
echo   1. cd phases\phase-1-collection
echo   2. python -m src.scraper
echo   3. cd ..\phase-2-processing
echo   4. python -m src.ingest
echo   5. cd ..\phase-5-frontend
echo   6. streamlit run app.py
pause
