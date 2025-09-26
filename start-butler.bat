@echo off
echo ============================================================
echo                  BUTLER System Launcher
echo            Texas Association of Counties
echo ============================================================
echo.

echo [1] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
echo Python found!
echo.

echo [2] Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ollama not found in PATH
    echo Please ensure Ollama is installed
    echo Download from: https://ollama.ai
    echo.
    echo Attempting to start anyway...
) else (
    echo Ollama found!
)
echo.

echo [3] Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may not have installed correctly
)
echo Dependencies checked!
echo.

echo [4] Starting Ollama service...
start "Ollama Service" /B ollama serve
echo Waiting for Ollama to start...
timeout /t 5 /nobreak >nul
echo.

echo [5] Checking for Llama model...
ollama list | findstr "llama3.2:latest" >nul 2>&1
if %errorlevel% neq 0 (
    echo Llama model not found. Pulling model (this may take a while)...
    ollama pull llama3.2:latest
)
echo Model ready!
echo.

echo [6] Starting BUTLER API Server...
start "BUTLER API" /B python ollama_with_docs.py
echo Waiting for API to initialize...
timeout /t 3 /nobreak >nul
echo.

echo [7] Opening BUTLER Interface...
start http://localhost:5019
echo.

echo ============================================================
echo           BUTLER System Started Successfully!
echo ============================================================
echo.
echo Access Points:
echo   - Web Interface: http://localhost:5019
echo   - API Status: http://localhost:5019/api/status
echo   - Main Interface: Open butler-final.html in browser
echo.
echo Press Ctrl+C to stop all services
echo ============================================================
echo.

pause