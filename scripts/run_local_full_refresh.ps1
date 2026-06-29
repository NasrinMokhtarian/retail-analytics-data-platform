param (
    [Parameter(Mandatory = $true)]
    [string]$OlistRunDate,

    [Parameter(Mandatory = $true)]
    [string]$SupplierRunDate,

    [Parameter(Mandatory = $true)]
    [string]$BrHolidaysRunDate,

    [string]$ValidationRunDate = $BrHolidaysRunDate,

    [string]$LogLevel = "INFO"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Starting Retail Analytics local full refresh..." -ForegroundColor Cyan
Write-Host "Olist run date: $OlistRunDate" -ForegroundColor Cyan
Write-Host "Supplier run date: $SupplierRunDate" -ForegroundColor Cyan
Write-Host "Brazil holidays run date: $BrHolidaysRunDate" -ForegroundColor Cyan
Write-Host "Validation run date: $ValidationRunDate" -ForegroundColor Cyan

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
        --pipeline-name "retail_local_full_refresh" `
        --run-date $ValidationRunDate `
        --selected-source olist supplier br_holidays).Trim()

    Write-Host "Pipeline run ID: $PipelineRunId" -ForegroundColor Cyan

    Write-Host "Step 1/8: Create PostgreSQL schemas" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.create_postgres_schemas `
        --log-level $LogLevel

    Write-Host "Step 2/8: Create load audit table" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.create_audit_table `
        --log-level $LogLevel

    Write-Host "Step 3/8: Validate PostgreSQL load configuration" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.validate_postgres_load_config `
        --olist-run-date $OlistRunDate `
        --supplier-run-date $SupplierRunDate `
        --br-holidays-run-date $BrHolidaysRunDate `
        --only olist supplier br_holidays `
        --log-level $LogLevel

    Write-Host "Step 4/8: Load cleaned files into PostgreSQL raw schema" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.load_cleaned_to_postgres `
        --olist-run-date $OlistRunDate `
        --supplier-run-date $SupplierRunDate `
        --br-holidays-run-date $BrHolidaysRunDate `
        --only olist supplier br_holidays `
        --log-level $LogLevel

    Write-Host "Step 5/8: Validate PostgreSQL loads" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.validate_postgres_loads `
        --olist-run-date $OlistRunDate `
        --supplier-run-date $SupplierRunDate `
        --br-holidays-run-date $BrHolidaysRunDate `
        --validation-run-date $ValidationRunDate `
        --only olist supplier br_holidays `
        --log-level $LogLevel

    $PostgresValidationReportPath = ".\reports\postgres_validation\run_date=$ValidationRunDate\postgres_load_validation_report.csv"

    Write-Host "Step 6/8: PostgreSQL validation gate" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.check_report_gates `
        --report-path $PostgresValidationReportPath `
        --log-level $LogLevel

    Write-Host "Step 7/8: Run dbt build" -ForegroundColor Yellow
    Push-Location ".\dbt_retail_analytics"

    try {
        if (-not (Test-Path $DbtExe)) {
            throw "dbt executable not found at $DbtExe."
        }

        & $DbtExe build
    }
    finally {
        Pop-Location
    }

    Write-Host "Step 8/8: Finish pipeline audit as SUCCESS" -ForegroundColor Yellow
    & $PythonExe -m retail_analytics.cli.pipeline_audit finish `
        --pipeline-run-id $PipelineRunId `
        --status SUCCESS

    Write-Host "Retail Analytics local full refresh completed successfully." -ForegroundColor Green
}
catch {
    $ErrorMessage = $_.Exception.Message

    Write-Host "Retail Analytics local full refresh failed." -ForegroundColor Red
    Write-Host $ErrorMessage -ForegroundColor Red

    if ($PipelineRunId) {
        & $PythonExe -m retail_analytics.cli.pipeline_audit finish `
            --pipeline-run-id $PipelineRunId `
            --status FAILED `
            --error-message $ErrorMessage
    }

    throw
}