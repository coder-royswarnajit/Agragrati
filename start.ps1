# Agragrati - Development Start Script (PowerShell)
# Usage: .\start.ps1 [backend|frontend|all]

param(
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"

function Start-Backend {
    Write-Host "🚀 Starting Backend (FastAPI)..." -ForegroundColor Cyan
    Push-Location backend
    if (-not (Test-Path "venv")) {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
    }
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt -q
    Write-Host "Backend running at http://localhost:8000" -ForegroundColor Green
    uvicorn main:app --reload --port 8000
    Pop-Location
}

function Start-Frontend {
    Write-Host "🚀 Starting Frontend (Vite)..." -ForegroundColor Cyan
    Push-Location frontend
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        npm install
    }
    Write-Host "Frontend running at http://localhost:5173" -ForegroundColor Green
    npm run dev
    Pop-Location
}

switch ($Mode.ToLower()) {
    "backend" {
        Start-Backend
    }
    "frontend" {
        Start-Frontend
    }
    "all" {
        Write-Host "Starting both services..." -ForegroundColor Cyan
        Write-Host "Run in separate terminals:" -ForegroundColor Yellow
        Write-Host "  Terminal 1: .\start.ps1 backend" -ForegroundColor White
        Write-Host "  Terminal 2: .\start.ps1 frontend" -ForegroundColor White
        Write-Host ""
        Write-Host "Or use Docker:" -ForegroundColor Yellow
        Write-Host "  docker-compose up --build" -ForegroundColor White
    }
    default {
        Write-Host "Usage: .\start.ps1 [backend|frontend|all]" -ForegroundColor Red
    }
}
