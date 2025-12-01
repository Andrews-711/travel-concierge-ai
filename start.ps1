# Travel Concierge - Quick Start Script
# This script helps you get started with the Travel Concierge application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Travel Concierge - Quick Start" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version
    Write-Host "✓ Docker Compose found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Compose not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ Python not found. You'll need it for local development." -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Options:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Full Docker setup (recommended for beginners)"
Write-Host "2. Local development setup (for developers)"
Write-Host "3. Exit"
Write-Host ""

$choice = Read-Host "Select an option (1-3)"

switch ($choice) {
    "1" {
        Write-Host "`nStarting Full Docker Setup..." -ForegroundColor Yellow
        
        # Check .env file
        if (-not (Test-Path ".env")) {
            Write-Host "Creating .env file from template..." -ForegroundColor Yellow
            Copy-Item ".env.example" ".env"
            Write-Host "✓ .env file created" -ForegroundColor Green
            Write-Host "⚠ Please edit .env and set your SECRET_KEY before proceeding!" -ForegroundColor Yellow
            Write-Host "You can generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'" -ForegroundColor Cyan
            $continue = Read-Host "Press Enter when ready to continue..."
        }
        
        # Start services
        Write-Host "`nStarting Docker services..." -ForegroundColor Yellow
        docker-compose up -d
        
        Write-Host "`nWaiting for services to be ready (30 seconds)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        
        # Pull LLM model
        Write-Host "`nPulling LLM model (this may take a while, ~4.5GB)..." -ForegroundColor Yellow
        Write-Host "Pulling llama3:8b..." -ForegroundColor Cyan
        docker exec -it travel_ollama ollama pull llama3:8b
        
        Write-Host "`n========================================" -ForegroundColor Green
        Write-Host "✓ Setup Complete!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "`nAccess the application:"
        Write-Host "  API: http://localhost:8080" -ForegroundColor Cyan
        Write-Host "  Docs: http://localhost:8080/docs" -ForegroundColor Cyan
        Write-Host "  Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
        Write-Host "`nView logs: docker-compose logs -f backend" -ForegroundColor Yellow
        Write-Host "Stop services: docker-compose down" -ForegroundColor Yellow
    }
    
    "2" {
        Write-Host "`nStarting Local Development Setup..." -ForegroundColor Yellow
        
        # Check .env file
        if (-not (Test-Path ".env")) {
            Copy-Item ".env.example" ".env"
            Write-Host "✓ .env file created. Please configure it!" -ForegroundColor Yellow
        }
        
        # Start infrastructure services only
        Write-Host "`nStarting infrastructure services (postgres, redis, chroma, ollama)..." -ForegroundColor Yellow
        docker-compose up -d postgres redis chroma ollama
        
        Write-Host "`nWaiting for services to be ready (30 seconds)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        
        # Pull LLM model
        Write-Host "`nPulling LLM model..." -ForegroundColor Yellow
        docker exec -it travel_ollama ollama pull llama3:8b
        
        # Setup Python environment
        Write-Host "`nSetting up Python environment..." -ForegroundColor Yellow
        if (-not (Test-Path "backend\venv")) {
            Set-Location backend
            python -m venv venv
            .\venv\Scripts\Activate.ps1
            pip install --upgrade pip
            pip install -r requirements.txt
            Set-Location ..
            Write-Host "✓ Python environment created" -ForegroundColor Green
        } else {
            Write-Host "✓ Python environment already exists" -ForegroundColor Green
        }
        
        Write-Host "`n========================================" -ForegroundColor Green
        Write-Host "✓ Setup Complete!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "`nTo start development:"
        Write-Host "  1. cd backend" -ForegroundColor Cyan
        Write-Host "  2. .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
        Write-Host "  3. uvicorn app.main:app --reload --host 0.0.0.0 --port 8080" -ForegroundColor Cyan
        Write-Host "`nThen access: http://localhost:8080/docs" -ForegroundColor Yellow
    }
    
    "3" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host "Invalid option. Exiting..." -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nFor more information, see README.md and docs/" -ForegroundColor Cyan
