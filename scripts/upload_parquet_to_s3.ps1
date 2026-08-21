param(
    [string]$BucketName = "retail-analytics-datalake-nasrin-dev-eu-central-1",
    [string]$AwsProfile = "retail-analytics-dev",
    [string]$LocalParquetRoot = "data\processed\parquet",
    [string]$S3Prefix = "processed/athena_parquet",
    [string]$UploadRunDate = "2026-06-16",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$LocalRoot = Join-Path $ProjectRoot $LocalParquetRoot

if (-not (Test-Path $LocalRoot)) {
    throw "Local Parquet root does not exist: $LocalRoot"
}

$LocalParquetFiles = Get-ChildItem $LocalRoot -Recurse -Filter "*.parquet" -File

if ($LocalParquetFiles.Count -eq 0) {
    throw "No Parquet files found under: $LocalRoot"
}

$ReportDir = Join-Path $ProjectRoot "reports\s3_parquet_upload\run_date=$UploadRunDate"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$ReportPath = Join-Path $ReportDir "s3_parquet_upload_report.csv"

$Destination = "s3://$BucketName/$S3Prefix/"

Write-Host "Uploading local Parquet layer to S3"
Write-Host "Local root: $LocalRoot"
Write-Host "Destination: $Destination"
Write-Host "AWS profile: $AwsProfile"
Write-Host "DryRun: $DryRun"
Write-Host ""

if ($DryRun) {
    aws s3 sync $LocalRoot $Destination `
        --profile $AwsProfile `
        --exclude "*" `
        --include "*.parquet" `
        --dryrun
}
else {
    aws s3 sync $LocalRoot $Destination `
        --profile $AwsProfile `
        --exclude "*" `
        --include "*.parquet"
}

$Rows = New-Object System.Collections.Generic.List[object]

foreach ($File in $LocalParquetFiles) {
    $RelativePath = $File.FullName.Substring($LocalRoot.Path.Length).TrimStart("\", "/")
    $S3Key = "$S3Prefix/$($RelativePath -replace "\\", "/")"

    $Rows.Add([PSCustomObject]@{
        upload_run_date = $UploadRunDate
        local_file      = $File.FullName
        local_bytes     = $File.Length
        s3_bucket       = $BucketName
        s3_key          = $S3Key
        dry_run         = [bool]$DryRun
    })
}

$Rows | Export-Csv -Path $ReportPath -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "Upload report written to:"
Write-Host $ReportPath
Write-Host ""
Write-Host "Local Parquet file count: $($LocalParquetFiles.Count)"
Write-Host "Local Parquet total bytes: $(($LocalParquetFiles | Measure-Object Length -Sum).Sum)"