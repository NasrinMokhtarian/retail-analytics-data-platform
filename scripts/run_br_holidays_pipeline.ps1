param (
    [Parameter(Mandatory = $true)]
    [string]$RunDate,

    [string]$LogLevel = "INFO"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Starting Br holidays local pipeline..." -ForegroundColor Cyan
Write-Host "Run date: $RunDate" -ForegroundColor Cyan

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$PythonExe = ".\.venv\Scripts\python.exe"
$DbtExe = "..\.venv\Scripts\dbt.exe"
$PipelineRunId = $null

if (-not (Test-Path $PythonExe)) {
    throw "Python virtual environment not found at $PythonExe. Please create/activate the project venv first."
}

try {
    Write-Host "Creating pipeline audit record..." -ForegroundColor Cyan

    $PipelineRunId = (& $PythonExe -m retail_analytics.cli.pipeline_audit start `
        --pipeline-name "br_holidays_local_pipeline" `
        --run-date $RunDate `
        --selected-source br_holidays).Trim()

    Write-Host "Pipeline run ID: $PipelineRunId" -ForegroundColor Cyan

    Write-Host "Step 1/8: Extract Br holidays API data" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.br_holidays_extract `
        --run-date $RunDate `
        --log-level $LogLevel

    Write-Host "Step 2/8: Clean Br holidays data" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.br_holidays_cleaning `
        --run-date $RunDate `
        --log-level $LogLevel

    Write-Host "Step 3/8: Run Br holidays quality checks" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.br_holidays_quality `
        --run-date $RunDate `
        --log-level $LogLevel

    $QualityReportPath = ".\reports\br_holidays_quality\run_date=$RunDate\br_holidays_quality_checks.csv"

    Write-Host "Step 4/8: Quality gate" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.check_report_gates `
        --report-path $QualityReportPath `
        --log-level $LogLevel

    Write-Host "Step 5/8: Run Br holidays cleaning validation" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.br_holidays_cleaning_validation `
        --run-date $RunDate `
        --log-level $LogLevel

    $ValidationReportPath = ".\reports\br_holidays_cleaning_validation\run_date=$RunDate\br_holidays_cleaning_validation_report.csv"

    Write-Host "Step 6/8: Validation gate" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.check_report_gates `
        --report-path $ValidationReportPath `
        --log-level $LogLevel

    Write-Host "Step 7/8: Load Br holidays into PostgreSQL" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.load_cleaned_to_postgres `
        --br-holidays-run-date $RunDate `
        --only br_holidays `
        --log-level $LogLevel

    Write-Host "Step 8/8: Build dbt holiday-aware models" -ForegroundColor Yellow

    Push-Location ".\dbt_retail_analytics"
    try {
        if (-not (Test-Path $DbtExe)) {
            throw "dbt executable not found at $DbtExe."
        }

        & $DbtExe build --select +fct_orders_holiday_context
    }
    finally {
        Pop-Location
    }

    & $PythonExe -m retail_analytics.cli.pipeline_audit finish `
        --pipeline-run-id $PipelineRunId `
        --status SUCCESS

    Write-Host "Br holidays local pipeline completed successfully." -ForegroundColor Green
}
catch {
    $ErrorMessage = $_.Exception.Message

    Write-Host "Br holidays local pipeline failed." -ForegroundColor Red
    Write-Host $ErrorMessage -ForegroundColor Red

    if ($PipelineRunId) {
        & $PythonExe -m retail_analytics.cli.pipeline_audit finish `
            --pipeline-run-id $PipelineRunId `
            --status FAILED `
            --error-message $ErrorMessage
    }

    throw
}


# to run this script:
# .\scripts\run_br_holidays_pipeline.ps1 -RunDate <like 2026-06-16>