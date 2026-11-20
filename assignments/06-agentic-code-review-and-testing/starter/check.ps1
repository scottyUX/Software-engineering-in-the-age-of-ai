# check.ps1 — run all guardrails locally (Windows / PowerShell)
# Usage: .\check.ps1

Write-Host "`n=== Formatting check (black) ===" -ForegroundColor Cyan
black --check main.py test_main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAILED: Run 'black main.py test_main.py' to auto-fix." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Lint (ruff) ===" -ForegroundColor Cyan
ruff check main.py test_main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAILED: Fix the issues above." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Tests (pytest) ===" -ForegroundColor Cyan
pytest
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAILED: Fix the failing tests above." -ForegroundColor Red
    exit 1
}

Write-Host "`nAll checks passed!" -ForegroundColor Green
