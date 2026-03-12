# Change to the script's directory
Set-Location $PSScriptRoot

# Check if manage.py exists
if (-not (Test-Path "manage.py")) {
    Write-Host "Error: manage.py not found in current directory" -ForegroundColor Red
    Write-Host "Current directory: $PWD" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Starting Django development server..." -ForegroundColor Cyan
Write-Host ""

# Run the Django server
python manage.py runserver
