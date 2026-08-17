param(
    [string]$BucketName = "retail-analytics-datalake-nasrin-dev-eu-central-1",
    [string]$AwsProfile = "retail-analytics-dev",
    [string]$DefinitionRunDate = "2026-06-16",
    [string]$OlistRunDate = "2026-05-26",
    [string]$SupplierRunDate = "2026-06-01",
    [string]$BrHolidaysRunDate = "2026-06-16",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."

$ReportDir = Join-Path $ProjectRoot "reports\aws_glue_table_definitions\run_date=$DefinitionRunDate"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$SnippetPath = Join-Path $ReportDir "processed_csv_table_definitions.tfvars.snippet"

function Convert-ToGlueColumnName {
    param([string]$Name)

    $clean = $Name.Trim().ToLowerInvariant()
    $clean = $clean -replace "[^a-z0-9_]", "_"
    $clean = $clean -replace "_+", "_"
    $clean = $clean.Trim("_")

    if ($clean -match "^[0-9]") {
        $clean = "col_$clean"
    }

    return $clean
}

function Get-HeaderColumns {
    param([string]$FilePath)

    $header = Get-Content $FilePath -First 1
    if ([string]::IsNullOrWhiteSpace($header)) {
        throw "Header is empty for file: $FilePath"
    }

    return $header.Split(",") | ForEach-Object {
        Convert-ToGlueColumnName $_
    }
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
    $tableName = "olist_$baseName"

    $TableSpecs.Add([PSCustomObject]@{
        TableName  = $tableName
        SourceName = "olist"
        RunDate    = $OlistRunDate
        LocalFile  = $File.FullName
        S3Prefix   = "processed/athena_csv/$tableName/run_date=$OlistRunDate/"
    })
}

foreach ($File in Get-ChildItem $SupplierPath -Filter "*.csv" -File) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($File.Name)
    $baseName = $baseName -replace "_clean$", ""
    $tableName = $baseName

    $TableSpecs.Add([PSCustomObject]@{
        TableName  = $tableName
        SourceName = "supplier"
        RunDate    = $SupplierRunDate
        LocalFile  = $File.FullName
        S3Prefix   = "processed/athena_csv/$tableName/run_date=$SupplierRunDate/"
    })
}

foreach ($File in Get-ChildItem $BrHolidaysPath -Filter "*.csv" -File) {
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($File.Name)
    $baseName = $baseName -replace "_clean$", ""
    $tableName = $baseName

    $TableSpecs.Add([PSCustomObject]@{
        TableName  = $tableName
        SourceName = "br_holidays"
        RunDate    = $BrHolidaysRunDate
        LocalFile  = $File.FullName
        S3Prefix   = "processed/athena_csv/$tableName/run_date=$BrHolidaysRunDate/"
    })
}

if ($TableSpecs.Count -eq 0) {
    throw "No CSV files found for Athena table preparation."
}

Write-Host "Preparing Athena-ready CSV files..."
Write-Host "Bucket: $BucketName"
Write-Host "DryRun: $DryRun"
Write-Host ""

foreach ($Spec in $TableSpecs) {
    $Destination = "s3://$BucketName/$($Spec.S3Prefix)data.csv"

    Write-Host "$($Spec.TableName)"
    Write-Host "  Local: $($Spec.LocalFile)"
    Write-Host "  S3:    $Destination"

    if ($DryRun) {
        aws s3 cp $Spec.LocalFile $Destination --profile $AwsProfile --dryrun
    }
    else {
        aws s3 cp $Spec.LocalFile $Destination --profile $AwsProfile
    }
}

$Lines = New-Object System.Collections.Generic.List[string]
$Lines.Add("processed_csv_table_definitions = {") | Out-Null

foreach ($Spec in ($TableSpecs | Sort-Object TableName)) {
    $Columns = Get-HeaderColumns $Spec.LocalFile

    $Lines.Add("  $($Spec.TableName) = {") | Out-Null
    $Lines.Add("    description = `"Athena external table for $($Spec.TableName) processed CSV data.`"") | Out-Null
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

Write-Host ""
Write-Host "Generated Terraform tfvars snippet:"
Write-Host $SnippetPath
Write-Host ""
Write-Host "Table count: $($TableSpecs.Count)"