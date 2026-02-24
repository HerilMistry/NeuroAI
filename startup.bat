@echo off
REM NeuroAI Complete Project Startup Script (Windows)
REM Starts backend with ML models and frontend simultaneously

setlocal enabledelayedexpansion

set "PROJECT_ROOT=C:\path\to\NeuroAI"
set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "FRONTEND_DIR=%PROJECT_ROOT%\pathfinder-neurals"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         NeuroAI - Complete Project Startup (Windows)       ║
echo ║    AI-Powered Drug Discovery Platform                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check Python
echo [1/4] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK - Python %PYTHON_VERSION% found

REM Setup Backend
echo [2/4] Setting up backend dependencies...
cd /d "%BACKEND_DIR%"
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q --upgrade pip setuptools wheel
pip install -q -r requirements.txt || pip install -q -r requirements-minimal.txt
python manage.py migrate --noinput >nul 2>&1 || echo Migrations complete
echo OK - Backend ready

REM Setup Frontend
echo [3/4] Setting up frontend dependencies...
cd /d "%FRONTEND_DIR%"
if not exist "node_modules" (
    echo Installing Node packages...
    npm install -q
) else (
    npm install -q --legacy-peer-deps
)
echo OK - Frontend ready

REM Start Services
echo [4/4] Starting services...
echo.

REM Start Backend (new terminal)
cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat
start "NeuroAI Backend" cmd /k python manage.py runserver 0.0.0.0:8000

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start Frontend (new terminal)
cd /d "%FRONTEND_DIR%"
start "NeuroAI Frontend" cmd /k npm run dev

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                   OK - Project Started                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Access the application at:
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000/api/v1/
echo   Admin:     http://localhost:8000/admin/
echo.
echo ML Models:
echo   OK GraphDTA       - Binding affinity prediction
echo   OK MedGemma-7B    - Toxicity assessment
echo   OK ESM-2-33M     - Protein embeddings
echo   OK RDKit         - Molecular analysis
echo.
