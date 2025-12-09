# Start Document Understanding System
# Run this script to start both backend and frontend

Write-Host "🚀 Starting Document Understanding System..." -ForegroundColor Cyan

# Start Backend
Write-Host "`n📦 Starting Backend API on http://localhost:1201..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python -m app.main"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "🎨 Starting Frontend UI on http://localhost:3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host "`n✅ System started!" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Backend API: http://localhost:1201" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:1201/docs" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C in each terminal to stop services." -ForegroundColor Gray
