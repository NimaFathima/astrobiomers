# Simple GitHub Push Script
# Push ASTROBIOMERS code to GitHub

Write-Host "Starting GitHub push..." -ForegroundColor Green

# Create .gitignore
$gitignoreContent = @"
# Environment files
.env
.env.local
.env.production
backend/.env
backend/.env.local
backend/.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
build/
.vscode/
.DS_Store

# Neo4j
.neo4j/
neo4j/
*.db

# Logs
*.log
logs/
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding utf8 -NoNewline
Write-Host "Created .gitignore" -ForegroundColor Green

# Initialize git if not already
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..." -ForegroundColor Cyan
    git init
    Write-Host "Git initialized" -ForegroundColor Green
}

# Add remote if not exists
$remoteExists = git remote -v 2>&1 | Select-String "origin"
if (-not $remoteExists) {
    Write-Host "Adding GitHub remote..." -ForegroundColor Cyan
    git remote add origin https://github.com/NimaFathima/astrobiomers.git
    Write-Host "Remote added" -ForegroundColor Green
}

# Stage all files
Write-Host "Staging files..." -ForegroundColor Cyan
git add .
Write-Host "Files staged" -ForegroundColor Green

# Commit
Write-Host "Creating commit..." -ForegroundColor Cyan
git commit -m "Deploy: NASA Space Apps 2024 - Biology Space Research Engine"
Write-Host "Commit created" -ForegroundColor Green

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "You may need to authenticate with GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host "`nDONE! Code pushed to: https://github.com/NimaFathima/astrobiomers" -ForegroundColor Green
Write-Host "`nNext steps will be provided..." -ForegroundColor Cyan
