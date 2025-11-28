# Installation Script untuk Windows
# Jalankan script ini untuk install semua dependencies

Write-Host "======================================"
Write-Host "Installing Dependencies"
Write-Host "======================================"

# Install Backend Dependencies
Write-Host ""
Write-Host "📦 Installing Backend Dependencies..."
Set-Location backend
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend dependencies installed successfully"
} else {
    Write-Host "❌ Failed to install backend dependencies"
    exit 1
}

Set-Location ..

# Install Frontend Dependencies
Write-Host ""
Write-Host "📦 Installing Frontend Dependencies..."
Set-Location frontend
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend dependencies installed successfully"
} else {
    Write-Host "❌ Failed to install frontend dependencies"
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "======================================"
Write-Host "✅ All dependencies installed!"
Write-Host "======================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Run './start.bat' to start both servers"
Write-Host "2. Open http://localhost:5173 in your browser"
Write-Host "======================================"
