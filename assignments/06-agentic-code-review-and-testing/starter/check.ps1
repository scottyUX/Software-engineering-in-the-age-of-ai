# Local guardrails for Windows PowerShell: the same three checks CI runs.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$steps = @(
    @("black (format)", "python -m black --check --diff ."),
    @("ruff (lint)", "python -m ruff check ."),
    @("pytest", "python -m pytest")
)
foreach ($s in $steps) {
    Write-Host "== $($s[0])"
    Invoke-Expression $s[1]
    if ($LASTEXITCODE -ne 0) { Write-Host "FAILED: $($s[0])"; exit $LASTEXITCODE }
}
Write-Host "All checks passed."
