# 🚀 Quick Deploy to Render Script

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     AstroBiomers - Render Deployment Helper        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Step 1: Check Git status
Write-Host "📋 Step 1: Checking Git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "✅ Found changes to commit" -ForegroundColor Green
    Write-Host $gitStatus
} else {
    Write-Host "⚠️  No changes detected" -ForegroundColor Yellow
}

# Step 2: Add all files
Write-Host "`n📦 Step 2: Adding deployment files..." -ForegroundColor Yellow
git add .

# Step 3: Commit
Write-Host "`n💾 Step 3: Committing changes..." -ForegroundColor Yellow
$commitMessage = "Add Render deployment configuration and CORS updates"
git commit -m $commitMessage
Write-Host "✅ Committed: $commitMessage" -ForegroundColor Green

# Step 4: Push to GitHub
Write-Host "`n🚀 Step 4: Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Successfully pushed to GitHub!" -ForegroundColor Green
    
    Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║              READY FOR RENDER DEPLOYMENT!             ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "📋 Next Steps on Render Dashboard:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Root Directory: backend" -ForegroundColor White
    Write-Host "2. Dockerfile Path: /Dockerfile" -ForegroundColor White
    Write-Host "3. Add Environment Variables:" -ForegroundColor White
    Write-Host "   - NEO4J_URI" -ForegroundColor Gray
    Write-Host "   - NEO4J_USER" -ForegroundColor Gray
    Write-Host "   - NEO4J_PASSWORD" -ForegroundColor Gray
    Write-Host "   - NEO4J_DATABASE = neo4j" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Click 'Create Web Service' ✨" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📚 Full guide: DEPLOYMENT_CHECKLIST.md" -ForegroundColor Cyan
    
} else {
    Write-Host "`n❌ Error pushing to GitHub" -ForegroundColor Red
    Write-Host "Please check your Git configuration and try again." -ForegroundColor Yellow
}

Write-Host "`n"
