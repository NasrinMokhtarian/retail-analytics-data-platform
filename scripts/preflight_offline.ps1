$ErrorActionPreference = "Stop"

Write-Host "=== Retail Analytics offline preflight ==="

Write-Host "`n[1/6] Python syntax"
python -m compileall -q src airflow/dags

Write-Host "`n[2/6] Python tests"
python -m pytest

Write-Host "`n[3/6] Redshift dbt parse/list"
Push-Location dbt
try {
    dbt parse --profiles-dir .
    dbt ls --profiles-dir . | Out-Null
}
finally {
    Pop-Location
}

Write-Host "`n[4/6] Docker Compose syntax"
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker compose config --quiet
} else {
    Write-Host "SKIP: docker command not installed."
}

Write-Host "`n[5/6] Terraform formatting/validation"
$tfRoot = "infra/terraform"
if ((Test-Path $tfRoot) -and (Get-Command terraform -ErrorAction SilentlyContinue)) {
    terraform -chdir=$tfRoot fmt -check -recursive

    $dev = "infra/terraform/environments/dev"
    if (Test-Path (Join-Path $dev ".terraform")) {
        terraform -chdir=$dev validate
    } else {
        Write-Host "SKIP validate: environments/dev has not been terraform init'd."
    }
} else {
    Write-Host "SKIP: Terraform tree or terraform executable not available."
}

Write-Host "`n[6/6] Git whitespace/secrets hygiene"
git diff --check

$trackedSensitive = git ls-files | Select-String -Pattern '(^|/)(\.env|profiles\.yml)$|\.tfstate(\.|$)|(^|/)[^/]*\.tfvars$'
if ($trackedSensitive) {
    Write-Host "ERROR: potentially sensitive/generated files are tracked:"
    $trackedSensitive | ForEach-Object { Write-Host "  $_" }
    exit 1
}

Write-Host "`nPASS: offline preflight completed."
