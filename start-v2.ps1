# Travel Concierge V2 - Quick Start Script
# Lightweight, stateless travel planning system

param(
    [switch]$Stop,
    [switch]$Logs,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

Write-Host "Travel Concierge V2 - Lightweight Edition" -ForegroundColor Cyan
Write-Host ("=" * 60)

if ($Stop) {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    docker-compose -f docker-compose-v2.yml down
    Write-Host "Services stopped" -ForegroundColor Green
    exit 0
}

if ($Clean) {
    Write-Host "`nCleaning up..." -ForegroundColor Yellow
    docker-compose -f docker-compose-v2.yml down -v
    Write-Host "Cleanup complete" -ForegroundColor Green
    exit 0
}

if ($Logs) {
    Write-Host "`nShowing logs..." -ForegroundColor Yellow
    docker-compose -f docker-compose-v2.yml logs -f
    exit 0
}

# Main startup flow
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    docker --version | Out-Null
    Write-Host "[OK] Docker installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path "backend_v2\.env")) {
    Write-Host "`nCreating .env file..." -ForegroundColor Yellow
    Copy-Item "backend_v2\.env.example" "backend_v2\.env"
    Write-Host "[OK] .env file created" -ForegroundColor Green
}

# Start services
Write-Host "`nStarting services (Ollama + Backend)..." -ForegroundColor Yellow
docker-compose -f docker-compose-v2.yml up -d

Write-Host "`nWaiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if Ollama is running
$ollamaRunning = docker ps --filter "name=travel_ollama" --filter "status=running" -q
if ($ollamaRunning) {
    Write-Host "[OK] Ollama service started" -ForegroundColor Green
    
    # Check if model exists
    Write-Host "`nChecking for LLM model..." -ForegroundColor Yellow
    $modelExists = docker exec travel_ollama ollama list 2>&1 | Select-String "llama3:8b"
    
    if (-not $modelExists) {
        Write-Host "Model not found. Downloading llama3:8b (~4.7GB)..." -ForegroundColor Yellow
        Write-Host "This may take 5-10 minutes depending on your internet speed..." -ForegroundColor Cyan
        docker exec travel_ollama ollama pull llama3:8b
        Write-Host "[OK] Model downloaded successfully" -ForegroundColor Green
    } else {
        Write-Host "[OK] Model llama3:8b already exists" -ForegroundColor Green
    }
} else {
    Write-Host "[ERROR] Ollama service failed to start" -ForegroundColor Red
    Write-Host "Check logs with: docker logs travel_ollama" -ForegroundColor Yellow
    exit 1
}

# Check backend
Start-Sleep -Seconds 3
$backendRunning = docker ps --filter "name=travel_backend" --filter "status=running" -q
if ($backendRunning) {
    Write-Host "[OK] Backend service started" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Backend service failed to start" -ForegroundColor Red
    Write-Host "Check logs with: docker logs travel_backend" -ForegroundColor Yellow
    exit 1
}

# Test API
Write-Host "`nTesting API..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -Method Get -TimeoutSec 10
    if ($response.status -eq "healthy") {
        Write-Host "[OK] API is healthy" -ForegroundColor Green
        Write-Host "   Ollama status: $($response.ollama)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "[INFO] API not responding yet (this is normal)" -ForegroundColor Yellow
    Write-Host "   Wait 30 seconds and try: http://localhost:8080/health" -ForegroundColor Cyan
}

# Success message
Write-Host "`n" + ("=" * 60) -ForegroundColor Green
Write-Host "SUCCESS: Travel Concierge V2 is running!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Green

Write-Host "`nAPI Endpoints:" -ForegroundColor Cyan
Write-Host "   - API Docs:    http://localhost:8080/docs" -ForegroundColor White
Write-Host "   - Health:      http://localhost:8080/health" -ForegroundColor White
Write-Host "   - Chat:        POST http://localhost:8080/chat" -ForegroundColor White
Write-Host "   - Plan Trip:   POST http://localhost:8080/plan" -ForegroundColor White
Write-Host "   - Upload Doc:  POST http://localhost:8080/upload" -ForegroundColor White

Write-Host "`nUseful Commands:" -ForegroundColor Cyan
Write-Host "   - View logs:       .\start-v2.ps1 -Logs" -ForegroundColor White
Write-Host "   - Stop services:   .\start-v2.ps1 -Stop" -ForegroundColor White
Write-Host "   - Clean up:        .\start-v2.ps1 -Clean" -ForegroundColor White
Write-Host "   - Restart:         .\start-v2.ps1" -ForegroundColor White

Write-Host "`nQuick Test:" -ForegroundColor Cyan
Write-Host '   $body = @{ message = "Best places in Paris?" } | ConvertTo-Json' -ForegroundColor White
Write-Host '   Invoke-RestMethod -Uri http://localhost:8080/chat -Method Post -Body $body -ContentType "application/json"' -ForegroundColor White

Write-Host "`nRead README-V2.md for full documentation" -ForegroundColor Yellow
Write-Host ""
