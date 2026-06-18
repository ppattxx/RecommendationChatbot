# ============================================================
# run-codex.ps1 - Jalankan OpenAI Codex CLI dengan API Key
# Usage: .\run-codex.ps1
# ============================================================

$env:OPENAI_API_KEY = "sk-t1pv6v-b5603724726d6e69ecb9fb947920d62a"

Write-Host "✅ OPENAI_API_KEY berhasil di-set untuk sesi ini." -ForegroundColor Green
Write-Host "🚀 Menjalankan Codex..." -ForegroundColor Cyan
Write-Host ""

codex
