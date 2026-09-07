$ErrorActionPreference = "Stop"

Write-Host "=== Final repository audit ==="

Write-Host "`n[1/6] Git status"
git status --short

Write-Host "`n[2/6] Git diff integrity"
git diff --check

Write-Host "`n[3/6] Sensitive tracked files"
$trackedSensitive = git ls-files | Select-String -Pattern '(^|/)(\.env|profiles\.yml)$|\.tfstate(\.|$)|(^|/)[^/]*\.tfvars$'
if ($trackedSensitive) {
    Write-Host "ERROR: potentially sensitive files are tracked:"
    $trackedSensitive | ForEach-Object { Write-Host "  $_" }
    exit 1
}
Write-Host "PASS: no obvious sensitive files tracked."

Write-Host "`n[4/6] dbt inventory"
Push-Location dbt
try {
    dbt parse --profiles-dir .
    $models = (dbt ls --resource-type model --profiles-dir . | Measure-Object -Line).Lines
    $tests = (dbt ls --resource-type test --profiles-dir . | Measure-Object -Line).Lines
    $sources = (dbt ls --resource-type source --profiles-dir . | Measure-Object -Line).Lines
    Write-Host "Models:  $models"
    Write-Host "Tests:   $tests"
    Write-Host "Sources: $sources"
    if ($models -ne 34 -or $tests -ne 39 -or $sources -ne 11) {
        throw "dbt inventory differs from validated checkpoint."
    }
}
finally {
    Pop-Location
}
Write-Host "PASS: dbt inventory matches."

Write-Host "`n[5/6] Python tests"
python -m pytest

Write-Host "`n[6/6] Docker/Terraform offline checks"
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker compose config --quiet
} else {
    Write-Host "SKIP: docker not installed."
}
if (Get-Command terraform -ErrorAction SilentlyContinue) {
    terraform -chdir=infra/terraform fmt -check -recursive
    if (Test-Path "infra/terraform/environments/dev/.terraform") {
        terraform -chdir=infra/terraform/environments/dev validate
    }
} else {
    Write-Host "SKIP: terraform not installed."
}

Write-Host "`nPASS: final repository audit completed."
Write-Host "No Redshift dbt build/test query was executed."
