# ============================================================
# run-codex.ps1 - Jalankan OpenAI Codex CLI dengan API Key
# Usage: .\run-codex.ps1
# ============================================================

$env:OPENAI_API_KEY = "sk-dpshfn-74a19aa2b3dd2f5dc66abcb5d91bc7ef"

Write-Host "✅ OPENAI_API_KEY berhasil di-set untuk sesi ini." -ForegroundColor Green
Write-Host "🚀 Menjalankan Codex..." -ForegroundColor Cyan
Write-Host ""

codex
