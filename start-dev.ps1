# ============================================================
# start-dev.ps1 - Jalankan Backend + Frontend secara bersamaan
# Usage: .\start-dev.ps1
#
# Session 1: Backend Flask  → http://localhost:5500
# Session 2: Frontend Vite  → http://localhost:3001
# ============================================================

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Chatbot Rekomendasi Restoran - Dev Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Backend  → http://localhost:5500" -ForegroundColor Yellow
Write-Host "  Frontend → http://localhost:3001" -ForegroundColor Yellow
Write-Host ""
Write-Host "Membuka 2 terminal terpisah..." -ForegroundColor Green
Write-Host ""

# ─── Session 1: Backend Flask ─────────────────────────────────
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "
    `$Host.UI.RawUI.WindowTitle = 'Backend - Flask API :5500';
    Set-Location '$ProjectRoot';
    Write-Host '============================================================' -ForegroundColor Cyan;
    Write-Host '   SESSION 1: Backend Flask API' -ForegroundColor Cyan;
    Write-Host '   Running on http://localhost:5500' -ForegroundColor Yellow;
    Write-Host '============================================================' -ForegroundColor Cyan;
    Write-Host '';
    python backend/main.py
    "
)

# Beri jeda agar backend sempat start lebih dulu
Start-Sleep -Seconds 2

# ─── Session 2: Frontend Vite ─────────────────────────────────
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "
    `$Host.UI.RawUI.WindowTitle = 'Frontend - Vite React :3001';
    Set-Location '$ProjectRoot\frontend';
    Write-Host '============================================================' -ForegroundColor Magenta;
    Write-Host '   SESSION 2: Frontend Vite + React' -ForegroundColor Magenta;
    Write-Host '   Running on http://localhost:3001' -ForegroundColor Yellow;
    Write-Host '============================================================' -ForegroundColor Magenta;
    Write-Host '';
    npm run dev
    "
)

Write-Host "✅ Kedua session berhasil dibuka!" -ForegroundColor Green
Write-Host ""
Write-Host "Tekan Enter untuk menutup launcher ini..." -ForegroundColor Gray
Read-Host
