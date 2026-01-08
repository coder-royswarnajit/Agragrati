@echo off
REM Agragrati - Development Start Script (Windows Batch)
REM Usage: start.bat [backend|frontend|docker]

if "%1"=="" goto help
if "%1"=="backend" goto backend
if "%1"=="frontend" goto frontend
if "%1"=="docker" goto docker
goto help

:backend
echo Starting Backend (FastAPI)...
cd backend
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
echo.
echo Backend running at http://localhost:8000
echo API Docs at http://localhost:8000/docs
echo.
uvicorn main:app --reload --port 8000
goto end

:frontend
echo Starting Frontend (Vite)...
cd frontend
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)
echo.
echo Frontend running at http://localhost:5173
echo.
call npm run dev
goto end

:docker
echo Starting with Docker Compose...
docker-compose up --build
goto end

:help
echo.
echo  Agragrati - AI Resume and Job Search Platform
echo  =============================================
echo.
echo  Usage: start.bat [command]
echo.
echo  Commands:
echo    backend   - Start FastAPI backend (port 8000)
echo    frontend  - Start Vite frontend (port 5173)
echo    docker    - Start both with Docker Compose
echo.
echo  For development, run in two separate terminals:
echo    Terminal 1: start.bat backend
echo    Terminal 2: start.bat frontend
echo.
echo  Or use Docker for production-like environment:
echo    start.bat docker
echo.
goto end

:end
