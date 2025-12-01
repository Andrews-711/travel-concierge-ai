# Test Script for Travel Concierge API
# Run this after setup to verify everything works

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Travel Concierge - System Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:8080"
$testEmail = "test@example.com"
$testPassword = "TestPass123!"
$token = ""

# Test 1: Health Check
Write-Host "Test 1: Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    if ($response.status -eq "healthy") {
        Write-Host "✓ Health check passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Health check failed" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
    Write-Host "Make sure the backend is running!" -ForegroundColor Yellow
    exit 1
}

# Test 2: Register User
Write-Host "`nTest 2: User Registration..." -ForegroundColor Yellow
try {
    $registerBody = @{
        email = $testEmail
        password = $testPassword
        full_name = "Test User"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method Post -Body $registerBody -ContentType "application/json"
    Write-Host "✓ User registration successful" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "⚠ User already exists (this is OK)" -ForegroundColor Yellow
    } else {
        Write-Host "✗ User registration failed: $_" -ForegroundColor Red
    }
}

# Test 3: Login
Write-Host "`nTest 3: User Login..." -ForegroundColor Yellow
try {
    $loginBody = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $response.access_token
    Write-Host "✓ Login successful" -ForegroundColor Green
    Write-Host "  Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed: $_" -ForegroundColor Red
    exit 1
}

# Test 4: Get Current User
Write-Host "`nTest 4: Get Current User..." -ForegroundColor Yellow
try {
    $headers = @{
        Authorization = "Bearer $token"
    }
    $response = Invoke-RestMethod -Uri "$baseUrl/auth/me" -Method Get -Headers $headers
    Write-Host "✓ Get current user successful" -ForegroundColor Green
    Write-Host "  Email: $($response.email)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Get current user failed: $_" -ForegroundColor Red
}

# Test 5: Plan a Trip
Write-Host "`nTest 5: Plan a Trip (this may take 5-15 seconds)..." -ForegroundColor Yellow
try {
    $headers = @{
        Authorization = "Bearer $token"
    }
    $tripBody = @{
        destination = "Tokyo"
        duration_days = 3
        budget = 30000
        currency = "INR"
        dietary_preferences = @("vegetarian")
        interests = @("museums", "markets")
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/itinerary/plan" -Method Post -Body $tripBody -ContentType "application/json" -Headers $headers
    Write-Host "✓ Trip planning successful" -ForegroundColor Green
    Write-Host "  Generated $($response.options.Count) itinerary options" -ForegroundColor Gray
    Write-Host "  Request ID: $($response.request_id)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Trip planning failed: $_" -ForegroundColor Red
    Write-Host "  This might fail if Ollama/LLM is not ready. Check: docker-compose logs ollama" -ForegroundColor Yellow
}

# Test 6: Chat Message
Write-Host "`nTest 6: Send Chat Message..." -ForegroundColor Yellow
try {
    $headers = @{
        Authorization = "Bearer $token"
    }
    $chatBody = @{
        message = "What is the best time to visit Tokyo?"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/chat/message" -Method Post -Body $chatBody -ContentType "application/json" -Headers $headers
    Write-Host "✓ Chat message successful" -ForegroundColor Green
    Write-Host "  Response: $($response.message.Substring(0, [Math]::Min(100, $response.message.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Chat message failed: $_" -ForegroundColor Red
}

# Test 7: Get My Trips
Write-Host "`nTest 7: Get My Trips..." -ForegroundColor Yellow
try {
    $headers = @{
        Authorization = "Bearer $token"
    }
    $response = Invoke-RestMethod -Uri "$baseUrl/itinerary/my-trips" -Method Get -Headers $headers
    Write-Host "✓ Get my trips successful" -ForegroundColor Green
    Write-Host "  Found $($response.Count) trip(s)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Get my trips failed: $_" -ForegroundColor Red
}

# Test 8: Metrics Endpoint
Write-Host "`nTest 8: Metrics Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/metrics" -Method Get -UseBasicParsing
    if ($response.Content -match "http_requests_total") {
        Write-Host "✓ Metrics endpoint working" -ForegroundColor Green
    } else {
        Write-Host "⚠ Metrics endpoint returned unexpected format" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Metrics endpoint failed: $_" -ForegroundColor Red
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "If all tests passed, your system is ready!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Visit API docs: http://localhost:8080/docs" -ForegroundColor Cyan
Write-Host "  2. Try the API examples in docs/API_EXAMPLES.md" -ForegroundColor Cyan
Write-Host "  3. Start building your frontend!" -ForegroundColor Cyan
Write-Host "`nFor monitoring:" -ForegroundColor Yellow
Write-Host "  - Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
Write-Host "  - Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "`nView logs: docker-compose logs -f backend" -ForegroundColor Yellow
