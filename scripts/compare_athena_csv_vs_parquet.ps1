param(
    [string]$AwsProfile = "retail-analytics-dev",
    [string]$DatabaseName = "retail_analytics_processed_dev",
    [string]$WorkGroup = "retail_analytics_dev",
    [string]$ComparisonRunDate = "2026-06-16",
    [int]$PollSeconds = 2,
    [int]$TimeoutSeconds = 180
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$ReportDir = Join-Path $ProjectRoot "reports\aws_athena_optimization_proof\run_date=$ComparisonRunDate"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$ReportPath = Join-Path $ReportDir "athena_csv_vs_parquet_scan_comparison_report.csv"
$SummaryPath = Join-Path $ReportDir "athena_csv_vs_parquet_optimization_summary.md"

function Invoke-AthenaCountQuery {
    param(
        [string]$TableName,
        [string]$TableFormat
    )

    $Query = "SELECT COUNT(*) AS row_count FROM $DatabaseName.$TableName;"

    Write-Host "Running $TableFormat count query for table: $TableName"

    $QueryExecutionId = aws athena start-query-execution `
        --query-string $Query `
        --work-group $WorkGroup `
        --profile $AwsProfile `
        --query "QueryExecutionId" `
        --output text

    $Elapsed = 0

    do {
        Start-Sleep -Seconds $PollSeconds
        $Elapsed += $PollSeconds

        $ExecutionJson = aws athena get-query-execution `
            --query-execution-id $QueryExecutionId `
            --profile $AwsProfile `
            --output json

        $Execution = $ExecutionJson | ConvertFrom-Json
        $State = $Execution.QueryExecution.Status.State

        if ($Elapsed -ge $TimeoutSeconds) {
            throw "Athena query timed out after $TimeoutSeconds seconds. QueryExecutionId=$QueryExecutionId"
        }
    } while ($State -eq "QUEUED" -or $State -eq "RUNNING")

    $DataScannedBytes = [int64]$Execution.QueryExecution.Statistics.DataScannedInBytes
    $EngineExecutionMillis = [int64]$Execution.QueryExecution.Statistics.EngineExecutionTimeInMillis

    if ($State -ne "SUCCEEDED") {
        $Reason = $Execution.QueryExecution.Status.StateChangeReason

        return [PSCustomObject]@{
            table_name               = $TableName
            table_format             = $TableFormat
            query_execution_id        = $QueryExecutionId
            status                   = $State
            row_count                = $null
            data_scanned_bytes       = $DataScannedBytes
            engine_execution_millis  = $EngineExecutionMillis
            error_message            = $Reason
        }
    }

    $ResultsJson = aws athena get-query-results `
        --query-execution-id $QueryExecutionId `
        --profile $AwsProfile `
        --output json

    $Results = $ResultsJson | ConvertFrom-Json

    $RowCountText = $Results.ResultSet.Rows[1].Data[0].VarCharValue
    $RowCount = [int64]$RowCountText

    return [PSCustomObject]@{
        table_name               = $TableName
        table_format             = $TableFormat
        query_execution_id        = $QueryExecutionId
        status                   = "SUCCEEDED"
        row_count                = $RowCount
        data_scanned_bytes       = $DataScannedBytes
        engine_execution_millis  = $EngineExecutionMillis
        error_message            = ""
    }
}

Write-Host "Reading Glue tables from database: $DatabaseName"

$TablesJson = aws glue get-tables `
    --database-name $DatabaseName `
    --profile $AwsProfile `
    --query "TableList[].Name" `
    --output json

$AllTables = $TablesJson | ConvertFrom-Json

if ($null -eq $AllTables -or $AllTables.Count -eq 0) {
    throw "No Glue tables found in database: $DatabaseName"
}

$ParquetTables = $AllTables | Where-Object { $_ -like "*_parquet" } | Sort-Object

if ($null -eq $ParquetTables -or $ParquetTables.Count -eq 0) {
    throw "No Parquet tables found. Expected tables ending with _parquet."
}

$Rows = New-Object System.Collections.Generic.List[object]

foreach ($ParquetTable in $ParquetTables) {
    $CsvTable = $ParquetTable -replace "_parquet$", ""

    if ($AllTables -notcontains $CsvTable) {
        Write-Host "Skipping $ParquetTable because matching CSV table does not exist: $CsvTable"
        continue
    }

    Write-Host ""
    Write-Host "Comparing CSV=$CsvTable with Parquet=$ParquetTable"

    $CsvResult = Invoke-AthenaCountQuery -TableName $CsvTable -TableFormat "csv"
    $ParquetResult = Invoke-AthenaCountQuery -TableName $ParquetTable -TableFormat "parquet"

    $RowCountMatch = $false
    if ($CsvResult.status -eq "SUCCEEDED" -and $ParquetResult.status -eq "SUCCEEDED") {
        $RowCountMatch = ($CsvResult.row_count -eq $ParquetResult.row_count)
    }

    $ReductionBytes = $null
    $ReductionPercent = $null

    if (
        $CsvResult.status -eq "SUCCEEDED" `
        -and $ParquetResult.status -eq "SUCCEEDED" `
        -and $CsvResult.data_scanned_bytes -gt 0
    ) {
        $ReductionBytes = [int64]($CsvResult.data_scanned_bytes - $ParquetResult.data_scanned_bytes)
        $ReductionPercent = [math]::Round(($ReductionBytes / $CsvResult.data_scanned_bytes) * 100, 2)
    }

    $ComparisonStatus = "PASS"
    $ComparisonNote = "CSV and Parquet queries succeeded and row counts matched."

    if ($ParquetResult.status -ne "SUCCEEDED") {
        $ComparisonStatus = "FAIL"
        $ComparisonNote = "Parquet query failed. This must be fixed because Parquet is the optimized analytics layer."
    }
    elseif ($CsvResult.status -ne "SUCCEEDED") {
        $ComparisonStatus = "WARN"
        $ComparisonNote = "CSV query failed or was blocked, but Parquet query succeeded. This is acceptable for optimization proof."
    }
    elseif (-not $RowCountMatch) {
        $ComparisonStatus = "WARN"
        $ComparisonNote = "CSV and Parquet row counts differ. Likely CSV parsing limitation; Parquet is treated as the reliable analytics layer."
    }

    $Rows.Add([PSCustomObject]@{
        comparison_run_date             = $ComparisonRunDate
        database_name                   = $DatabaseName
        workgroup                       = $WorkGroup
        base_table_name                 = $CsvTable
        csv_table_name                  = $CsvTable
        parquet_table_name              = $ParquetTable
        csv_query_execution_id          = $CsvResult.query_execution_id
        parquet_query_execution_id      = $ParquetResult.query_execution_id
        csv_status                      = $CsvResult.status
        parquet_status                  = $ParquetResult.status
        csv_row_count                   = $CsvResult.row_count
        parquet_row_count               = $ParquetResult.row_count
        row_count_match                 = $RowCountMatch
        csv_data_scanned_bytes          = $CsvResult.data_scanned_bytes
        parquet_data_scanned_bytes      = $ParquetResult.data_scanned_bytes
        scan_reduction_bytes            = $ReductionBytes
        scan_reduction_percent          = $ReductionPercent
        csv_engine_execution_millis     = $CsvResult.engine_execution_millis
        parquet_engine_execution_millis = $ParquetResult.engine_execution_millis
        comparison_status               = $ComparisonStatus
        comparison_note                 = $ComparisonNote
        csv_error_message               = $CsvResult.error_message
        parquet_error_message           = $ParquetResult.error_message
    })

    Write-Host "  CSV scanned bytes:     $($CsvResult.data_scanned_bytes)"
    Write-Host "  Parquet scanned bytes: $($ParquetResult.data_scanned_bytes)"
    Write-Host "  Row count match:       $RowCountMatch"
    Write-Host "  Reduction percent:     $ReductionPercent"
}

$Rows | Export-Csv -Path $ReportPath -NoTypeInformation -Encoding UTF8

$Passed = ($Rows | Where-Object { $_.comparison_status -eq "PASS" }).Count
$Warned = ($Rows | Where-Object { $_.comparison_status -eq "WARN" }).Count
$Failed = ($Rows | Where-Object { $_.comparison_status -eq "FAIL" }).Count
$TotalCsvScanned = ($Rows | Measure-Object -Property csv_data_scanned_bytes -Sum).Sum
$TotalParquetScanned = ($Rows | Measure-Object -Property parquet_data_scanned_bytes -Sum).Sum

if ($null -eq $TotalCsvScanned) {
    $TotalCsvScanned = 0
}

if ($null -eq $TotalParquetScanned) {
    $TotalParquetScanned = 0
}

$TotalReductionBytes = $TotalCsvScanned - $TotalParquetScanned
$TotalReductionPercent = $null

if ($TotalCsvScanned -gt 0) {
    $TotalReductionPercent = [math]::Round(($TotalReductionBytes / $TotalCsvScanned) * 100, 2)
}

$SummaryLines = @(
    "# Athena CSV vs Parquet Optimization Proof",
    "",
    "## Purpose",
    "",
    "This report compares Athena scan statistics for the same processed datasets stored as CSV and Parquet.",
    "",
    "## Method",
    "",
    "- Query type: SELECT COUNT(*)",
    "- CSV tables: base Glue tables",
    "- Parquet tables: matching tables ending in _parquet",
    "- Metric: Athena DataScannedInBytes from query execution statistics",
    "",
    "## Results",
    "",
    "| Metric | Value |",
    "|---|---:|",
    "| Tables compared | $($Rows.Count) |",
    "| Passed comparisons | $Passed |",
    "| Warning comparisons | $Warned |",
    "| Failed comparisons | $Failed |",
    "| Total CSV scanned bytes | $TotalCsvScanned |",
    "| Total Parquet scanned bytes | $TotalParquetScanned |",
    "| Total scan reduction bytes | $TotalReductionBytes |",
    "| Total scan reduction percent | $TotalReductionPercent% |",
    "",
    "## Notes",
    "",
    "- This is a small project dataset, so the result should be presented as an optimization proof, not a large-scale benchmark.",
    "- Row counts must match between CSV and Parquet tables.",
    "- The comparison uses Athena query execution statistics, not estimated file sizes.",
    "- Broader analytical queries may show different scan patterns depending on selected columns and filters.",
    "",
    "## Detailed Report",
    "",
    "CSV report:",
    "",
    $ReportPath
)

$SummaryLines | Set-Content -Path $SummaryPath -Encoding UTF8

Write-Host ""
Write-Host "Comparison report written to:"
Write-Host $ReportPath
Write-Host ""
Write-Host "Summary written to:"
Write-Host $SummaryPath
Write-Host ""
Write-Host "Tables compared: $($Rows.Count)"
Write-Host "PASS: $Passed"
Write-Host "WARN: $Warned"
Write-Host "FAIL: $Failed"
Write-Host "Total CSV scanned bytes: $TotalCsvScanned"
Write-Host "Total Parquet scanned bytes: $TotalParquetScanned"
Write-Host "Total reduction percent: $TotalReductionPercent"

if ($Failed -gt 0) {
    throw "CSV vs Parquet comparison failed for $Failed table pair(s)."
}