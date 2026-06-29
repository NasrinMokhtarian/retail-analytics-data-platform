param (
    [Parameter(Mandatory = $true)]
    [string]$RunDate,

    [string]$LogLevel = "INFO"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Starting Brazil holidays local pipeline..." -ForegroundColor Cyan
Write-Host "Run date: $RunDate" -ForegroundColor Cyan

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$PythonExe = ".\.venv\Scripts\python.exe"
$DbtExe = "..\.venv\Scripts\dbt.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Python virtual environment not found at $PythonExe. Please create/activate the project venv first."
}

Write-Host "Step 1/6: Extract Brazil holidays API data" -ForegroundColor Yellow
& $PythonExe -m retail_analytics.cli.br_holidays_extract `
    --run-date $RunDate `
    --log-level $LogLevel

Write-Host "Step 2/6: Clean Brazil holidays data" -ForegroundColor Yellow
& $PythonExe -m retail_analytics.cli.br_holidays_cleaning `
    --run-date $RunDate `
    --log-level $LogLevel

Write-Host "Step 3/6: Run Brazil holidays quality checks" -ForegroundColor Yellow
& $PythonExe -m retail_analytics.cli.br_holidays_quality `
    --run-date $RunDate `
    --log-level $LogLevel

Write-Host "Step 4/6: Run Brazil holidays cleaning validation" -ForegroundColor Yellow
& $PythonExe -m retail_analytics.cli.br_holidays_cleaning_validation `
    --run-date $RunDate `
    --log-level $LogLevel

Write-Host "Step 5/6: Load Brazil holidays into PostgreSQL" -ForegroundColor Yellow
& $PythonExe -m retail_analytics.cli.load_cleaned_to_postgres `
    --br-holidays-run-date $RunDate `
    --only br_holidays `
    --log-level $LogLevel

Write-Host "Step 6/6: Build dbt holiday-aware models" -ForegroundColor Yellow
Push-Location ".\dbt_retail_analytics"

if (-not (Test-Path $DbtExe)) {
    throw "dbt executable not found at $DbtExe."
}

& $DbtExe build --select +fct_orders_holiday_context

Pop-Location

Write-Host "Brazil holidays local pipeline completed successfully." -ForegroundColor Green



#  command to run the script is:
# run_br_holidays_pipeline.ps1 -RunDate <run_date like 2026-06-16>

# Expected flow:
# 1. API extraction succeeds
# 2. cleaning succeeds
# 3. quality report is generated
# 4. validation report is generated
# 5. raw.br_holidays is loaded
# 6. dbt holiday-aware models build

# The dbt command uses:
# dbt build --select +fct_orders_holiday_context


# more tips:
# If you see an execution policy error, run this once in the same terminal:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# then run:
# .\scripts\run_br_holidays_pipeline.ps1 -RunDate <run_date like 2026-06-16>