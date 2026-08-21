param(
    [string]$DefinitionRunDate = "2026-06-16",
    [string]$OlistRunDate = "2026-05-26",
    [string]$SupplierRunDate = "2026-06-01",
    [string]$BrHolidaysRunDate = "2026-06-16",
    [string]$S3PrefixRoot = "processed/athena_parquet"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."

$ReportDir = Join-Path $ProjectRoot "reports\aws_glue_parquet_table_definitions\run_date=$DefinitionRunDate"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$SnippetPath = Join-Path $ReportDir "processed_parquet_table_definitions.tfvars.snippet"

function Convert-ToGlueColumnName {
    param([string]$Name)

    $clean = $Name.Trim().ToLowerInvariant()
    $clean = $clean -replace "[^a-z0-9_]", "_"
    $clean = $clean -replace "_+", "_"
    $clean = $clean.Trim("_")

    if ($clean -match "^[0-9]") {
        $clean = "col_$clean"
    }

    if ([string]::IsNullOrWhiteSpace($clean)) {
        throw "Column name became empty after normalization: $Name"
    }

    return $clean
}

function Get-HeaderColumns {
    param([string]$FilePath)

    $header = Get-Content $FilePath -First 1

    if ([string]::IsNullOrWhiteSpace($header)) {
        throw "Header is empty for file: $FilePath"
    }

    $columns = $header.Split(",") | ForEach-Object {
        Convert-ToGlueColumnName $_
    }

    $duplicateColumns = $columns |
        Group-Object |
        Where-Object { $_.Count -gt 1 } |
        Select-Object -ExpandProperty Name

    if ($duplicateColumns.Count -gt 0) {
        throw "Duplicate normalized columns found in ${FilePath}: $($duplicateColumns -join ', ')"    }

    return $columns
}

$TableSpecs = New-Object System.Collections.Generic.List[object]

$OlistPath = Join-Path $ProjectRoot "data\processed\olist_clean\run_date=$OlistRunDate"
$SupplierPath = Join-Path $ProjectRoot "data\processed\supplier_clean\run_date=$SupplierRunDate"
$BrHolidaysPath = Join-Path $ProjectRoot "data\processed\br_holidays_clean\run_date=$BrHolidaysRunDate"

if (-not (Test-Path $OlistPath)) {
    throw "Missing Olist cleaned folder: $OlistPath"
}

if (-not (Test-Path $SupplierPath)) {
    throw "Missing supplier cleaned folder: $SupplierPath"
}

if (-not (Test-Path $BrHolidaysPath)) {
    throw "Missing Brazil holidays cleaned folder: $BrHolidaysPath"
}

foreach ($File in Get-ChildItem $OlistPath -Filter "*.csv" -File) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($File.Name)
    $baseName = $baseName -replace "_clean$", ""

    $baseTableName = "olist_$baseName"
    $parquetTableName = "${baseTableName}_parquet"

    $TableSpecs.Add([PSCustomObject]@{
        TableName = $parquetTableName
        BaseTableName = $baseTableName
        SourceName = "olist"
        RunDate = $OlistRunDate
        LocalCsvFile = $File.FullName
        S3Prefix = "$S3PrefixRoot/$baseTableName/run_date=$OlistRunDate/"
    })
}

foreach ($File in Get-ChildItem $SupplierPath -Filter "*.csv" -File) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($File.Name)
    $baseName = $baseName -replace "_clean$", ""

    $baseTableName = $baseName
    $parquetTableName = "${baseTableName}_parquet"

    $TableSpecs.Add([PSCustomObject]@{
        TableName = $parquetTableName
        BaseTableName = $baseTableName
        SourceName = "supplier"
        RunDate = $SupplierRunDate
        LocalCsvFile = $File.FullName
        S3Prefix = "$S3PrefixRoot/$baseTableName/run_date=$SupplierRunDate/"
    })
}

foreach ($File in Get-ChildItem $BrHolidaysPath -Filter "*.csv" -File) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($File.Name)
    $baseName = $baseName -replace "_clean$", ""

    $baseTableName = $baseName
    $parquetTableName = "${baseTableName}_parquet"

    $TableSpecs.Add([PSCustomObject]@{
        TableName = $parquetTableName
        BaseTableName = $baseTableName
        SourceName = "br_holidays"
        RunDate = $BrHolidaysRunDate
        LocalCsvFile = $File.FullName
        S3Prefix = "$S3PrefixRoot/$baseTableName/run_date=$BrHolidaysRunDate/"
    })
}

if ($TableSpecs.Count -eq 0) {
    throw "No source CSV files found for Parquet Glue table preparation."
}

$Lines = New-Object System.Collections.Generic.List[string]
$Lines.Add("processed_parquet_table_definitions = {") | Out-Null

foreach ($Spec in ($TableSpecs | Sort-Object TableName)) {
    $Columns = Get-HeaderColumns $Spec.LocalCsvFile

    $Lines.Add("  $($Spec.TableName) = {") | Out-Null
    $Lines.Add("    description = `"Athena external table for $($Spec.BaseTableName) Parquet data.`"") | Out-Null
    $Lines.Add("    s3_prefix   = `"$($Spec.S3Prefix)`"") | Out-Null
    $Lines.Add("    columns = [") | Out-Null

    foreach ($Column in $Columns) {
        $Lines.Add("      { name = `"$Column`", type = `"string`" },") | Out-Null
    }

    $Lines.Add("    ]") | Out-Null
    $Lines.Add("  }") | Out-Null
}

$Lines.Add("}") | Out-Null

$Lines | Set-Content -Path $SnippetPath -Encoding UTF8

Write-Host "Generated Parquet Glue table tfvars snippet:"
Write-Host $SnippetPath
Write-Host ""
Write-Host "Parquet table count: $($TableSpecs.Count)"