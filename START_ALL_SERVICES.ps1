# 🚀 AstroBiomers - Start All Services
# Run this script to launch the complete application

Write-Host "`n╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🌌 ASTROBIOMERS STARTUP SCRIPT 🌌  ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "This will start:" -ForegroundColor White
Write-Host "  1. Backend API (port 8000)" -ForegroundColor Gray
Write-Host "  2. Frontend UI (port 8081)" -ForegroundColor Gray
Write-Host "  3. API Adapter (port 5000)`n" -ForegroundColor Gray

Write-Host "Press any key to continue or Ctrl+C to cancel..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "`n🚀 Starting services...`n" -ForegroundColor Cyan

# Stop any existing jobs
Get-Job | Remove-Job -Force 2>$null

# 1. Start Backend (FastAPI)
Write-Host "[1/3] Starting Backend API..." -ForegroundColor Yellow
Start-Job -ScriptBlock {
    Set-Location 'C:\Users\mi\Downloads\ASTROBIOMERS'
    python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
} -Name "Backend" | Out-Null

Start-Sleep -Seconds 3

# 2. Start Frontend (Vite + React)
Write-Host "[2/3] Starting Frontend UI..." -ForegroundColor Yellow
Start-Job -ScriptBlock {
    Set-Location 'C:\Users\mi\Downloads\ASTROBIOMERS\frontend\new frontend'
    npm run dev
} -Name "Frontend" | Out-Null

Start-Sleep -Seconds 3

# 3. Start API Adapter (Flask)
Write-Host "[3/3] Starting API Adapter..." -ForegroundColor Yellow
Start-Job -ScriptBlock {
    Set-Location 'C:\Users\mi\Downloads\ASTROBIOMERS\frontend'
    python api_adapter.py
} -Name "Adapter" | Out-Null

Write-Host "`n⏳ Services are starting (this takes ~30 seconds)...`n" -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Show running jobs
Write-Host "📊 Service Status:" -ForegroundColor Cyan
Get-Job | Format-Table Id, State, Name -AutoSize

Write-Host "`n✨ Startup complete! Services are warming up...`n" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host "`n🌐 Access Points:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:8081" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Adapter:   http://localhost:5000/api/health`n" -ForegroundColor White

Write-Host "⏳ Wait 30 seconds for full initialization, then open:" -ForegroundColor Yellow
Write-Host "   http://localhost:8081`n" -ForegroundColor Cyan

Write-Host "📝 Useful Commands:" -ForegroundColor Cyan
Write-Host "  Check status:  Get-Job | Format-Table" -ForegroundColor Gray
Write-Host "  View logs:     Receive-Job -Id <ID> -Keep" -ForegroundColor Gray
Write-Host "  Stop all:      Get-Job | Stop-Job; Get-Job | Remove-Job`n" -ForegroundColor Gray

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "`n🚀 Ready to explore space biology research!`n" -ForegroundColor Green

# Optional: Open browser after delay
Start-Sleep -Seconds 20
Write-Host "🌐 Opening application in browser..." -ForegroundColor Cyan
Start-Process "http://localhost:8081"

Write-Host "`n✅ Application launched!`n" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop all services when done.`n" -ForegroundColor Yellow

# Keep script alive so user can see jobs
while ($true) {
    Start-Sleep -Seconds 60
    $jobStatus = Get-Job | Where-Object { $_.State -ne "Running" }
    if ($jobStatus) {
        Write-Host "`n⚠️  Warning: Some services stopped:" -ForegroundColor Yellow
        $jobStatus | Format-Table Id, State, Name -AutoSize
        Write-Host "Run this script again to restart.`n" -ForegroundColor Gray
        break
    }
}
