# Test the ML Inference Service Demo
# This script tests all endpoints

Write-Host "Testing ML Inference Service Demo" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Test 1: Root endpoint
Write-Host "Test 1: Root endpoint" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/"
    $response | ConvertTo-Json -Depth 3
    Write-Host "✓ Root endpoint working" -ForegroundColor Green
} catch {
    Write-Host "✗ Root endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Health endpoint
Write-Host "Test 2: Health endpoint (liveness probe)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health"
    $response | ConvertTo-Json
    Write-Host "✓ Health endpoint working" -ForegroundColor Green
} catch {
    Write-Host "✗ Health endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Ready endpoint
Write-Host "Test 3: Ready endpoint (readiness probe)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/ready"
    $response | ConvertTo-Json
    Write-Host "✓ Ready endpoint working" -ForegroundColor Green
} catch {
    Write-Host "✗ Ready endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Prediction endpoint - Setosa (small petal)
Write-Host "Test 4: Prediction - Setosa (small petal length)" -ForegroundColor Yellow
try {
    $body = @{
        features = @(5.1, 3.5, 1.4, 0.2)
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/predict" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
    
    $response | ConvertTo-Json -Depth 3
    Write-Host "✓ Prediction endpoint working - Predicted: $($response.prediction)" -ForegroundColor Green
} catch {
    Write-Host "✗ Prediction failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 5: Prediction endpoint - Versicolor (medium petal)
Write-Host "Test 5: Prediction - Versicolor (medium petal length)" -ForegroundColor Yellow
try {
    $body = @{
        features = @(6.0, 2.9, 4.5, 1.5)
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/predict" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
    
    $response | ConvertTo-Json -Depth 3
    Write-Host "✓ Prediction endpoint working - Predicted: $($response.prediction)" -ForegroundColor Green
} catch {
    Write-Host "✗ Prediction failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 6: Prediction endpoint - Virginica (large petal)
Write-Host "Test 6: Prediction - Virginica (large petal length)" -ForegroundColor Yellow
try {
    $body = @{
        features = @(7.2, 3.0, 5.8, 1.6)
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/predict" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
    
    $response | ConvertTo-Json -Depth 3
    Write-Host "✓ Prediction endpoint working - Predicted: $($response.prediction)" -ForegroundColor Green
} catch {
    Write-Host "✗ Prediction failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "=================================" -ForegroundColor Green
Write-Host "All tests completed!" -ForegroundColor Green
Write-Host ""
Write-Host "To view interactive API documentation, open:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/docs" -ForegroundColor Cyan
