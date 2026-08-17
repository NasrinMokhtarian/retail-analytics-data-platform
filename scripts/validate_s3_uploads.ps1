param(
    [string]$BucketName = "retail-analytics-datalake-nasrin-dev-eu-central-1",
    [string]$AwsProfile = "retail-analytics-dev",
    [string]$ValidationRunDate = "2026-06-16",
    [string]$OlistRunDate = "2026-05-26",
    [string]$SupplierRunDate = "2026-06-01",
    [string]$BrHolidaysRunDate = "2026-06-16"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."

$ReportDir = Join-Path $ProjectRoot "reports\aws_s3_upload_validation\run_date=$ValidationRunDate"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$ReportPath = Join-Path $ReportDir "s3_upload_validation_report.csv"

$Sources = @(
    @{
        SourceName = "olist_clean"
        RunDate    = $OlistRunDate
        LocalPath  = Join-Path $ProjectRoot "data\processed\olist_clean\run_date=$OlistRunDate"
        S3Prefix   = "processed/olist_clean/run_date=$OlistRunDate/"
    },
    @{
        SourceName = "supplier_clean"
        RunDate    = $SupplierRunDate
        LocalPath  = Join-Path $ProjectRoot "data\processed\supplier_clean\run_date=$SupplierRunDate"
        S3Prefix   = "processed/supplier_clean/run_date=$SupplierRunDate/"
    },
    @{
        SourceName = "br_holidays_clean"
        RunDate    = $BrHolidaysRunDate
        LocalPath  = Join-Path $ProjectRoot "data\processed\br_holidays_clean\run_date=$BrHolidaysRunDate"
        S3Prefix   = "processed/br_holidays_clean/run_date=$BrHolidaysRunDate/"
    }
)

$Rows = New-Object System.Collections.Generic.List[object]

function Add-ValidationRow {
    param(
        [string]$SourceName,
        [string]$RunDate,
        [string]$CheckName,
        [string]$Status,
        [string]$Severity,
        [string]$LocalPath,
        [string]$S3Uri,
        [string]$FileName = "",
        [Nullable[int64]]$LocalSizeBytes = $null,
        [Nullable[int64]]$S3SizeBytes = $null,
        [Nullable[int]]$LocalFileCount = $null,
        [Nullable[int]]$S3FileCount = $null,
        [string]$Details = ""
    )

    $Rows.Add([PSCustomObject]@{
        validation_run_date = $ValidationRunDate
        source_name         = $SourceName
        source_run_date     = $RunDate
        check_name          = $CheckName
        status              = $Status
        severity            = $Severity
        local_path          = $LocalPath
        s3_uri              = $S3Uri
        file_name           = $FileName
        local_size_bytes    = $LocalSizeBytes
        s3_size_bytes       = $S3SizeBytes
        local_file_count    = $LocalFileCount
        s3_file_count       = $S3FileCount
        details             = $Details
    })
}

foreach ($Source in $Sources) {
    $SourceName = $Source.SourceName
    $RunDate = $Source.RunDate
    $LocalPath = $Source.LocalPath
    $S3Prefix = $Source.S3Prefix
    $S3Uri = "s3://$BucketName/$S3Prefix"

    Write-Host "Validating $SourceName ..."
    Write-Host "Local: $LocalPath"
    Write-Host "S3:    $S3Uri"

    if (-not (Test-Path $LocalPath)) {
        Add-ValidationRow `
            -SourceName $SourceName `
            -RunDate $RunDate `
            -CheckName "LOCAL_PATH_EXISTS" `
            -Status "FAIL" `
            -Severity "ERROR" `
            -LocalPath $LocalPath `
            -S3Uri $S3Uri `
            -Details "Local cleaned output folder does not exist."

        continue
    }

    Add-ValidationRow `
        -SourceName $SourceName `
        -RunDate $RunDate `
        -CheckName "LOCAL_PATH_EXISTS" `
        -Status "PASS" `
        -Severity "INFO" `
        -LocalPath $LocalPath `
        -S3Uri $S3Uri `
        -Details "Local cleaned output folder exists."

    $LocalFiles = Get-ChildItem -Path $LocalPath -File -Recurse

    $LocalFileMap = @{}
    foreach ($File in $LocalFiles) {
        $RelativePath = $File.FullName.Substring($LocalPath.Length).TrimStart("\", "/")
        $RelativePath = $RelativePath -replace "\\", "/"
        $ExpectedKey = "$S3Prefix$RelativePath"

        $LocalFileMap[$ExpectedKey] = @{
            RelativePath = $RelativePath
            SizeBytes    = [int64]$File.Length
            FullName     = $File.FullName
        }
    }

    $LocalFileCount = $LocalFiles.Count
    $LocalTotalBytes = ($LocalFiles | Measure-Object -Property Length -Sum).Sum
    if ($null -eq $LocalTotalBytes) {
        $LocalTotalBytes = 0
    }

    $ListResultJson = aws s3api list-objects-v2 `
        --bucket $BucketName `
        --prefix $S3Prefix `
        --profile $AwsProfile `
        --output json

    $ListResult = $ListResultJson | ConvertFrom-Json

    $S3Objects = @()
    if ($null -ne $ListResult.Contents) {
        $S3Objects = @($ListResult.Contents | Where-Object { $_.Size -gt 0 })
    }

    $S3ObjectMap = @{}
    foreach ($Object in $S3Objects) {
        $S3ObjectMap[$Object.Key] = [int64]$Object.Size
    }

    $S3FileCount = $S3Objects.Count
    $S3TotalBytes = ($S3Objects | Measure-Object -Property Size -Sum).Sum
    if ($null -eq $S3TotalBytes) {
        $S3TotalBytes = 0
    }

    if ($S3FileCount -gt 0) {
        Add-ValidationRow `
            -SourceName $SourceName `
            -RunDate $RunDate `
            -CheckName "S3_PREFIX_HAS_OBJECTS" `
            -Status "PASS" `
            -Severity "INFO" `
            -LocalPath $LocalPath `
            -S3Uri $S3Uri `
            -LocalFileCount $LocalFileCount `
            -S3FileCount $S3FileCount `
            -Details "S3 prefix contains uploaded objects."
    }
    else {
        Add-ValidationRow `
            -SourceName $SourceName `
            -RunDate $RunDate `
            -CheckName "S3_PREFIX_HAS_OBJECTS" `
            -Status "FAIL" `
            -Severity "ERROR" `
            -LocalPath $LocalPath `
            -S3Uri $S3Uri `
            -LocalFileCount $LocalFileCount `
            -S3FileCount $S3FileCount `
            -Details "S3 prefix does not contain uploaded data objects."
    }

    if ($LocalFileCount -eq $S3FileCount) {
        Add-ValidationRow `
            -SourceName $SourceName `
            -RunDate $RunDate `
            -CheckName "FILE_COUNT_MATCH" `
            -Status "PASS" `
            -Severity "INFO" `
            -LocalPath $LocalPath `
            -S3Uri $S3Uri `
            -LocalFileCount $LocalFileCount `
            -S3FileCount $S3FileCount `
            -Details "Local file count matches S3 object count."
    }
    else {
        Add-ValidationRow `
            -SourceName $SourceName `
            -RunDate $RunDate `
            -CheckName "FILE_COUNT_MATCH" `
            -Status "FAIL" `
            -Severity "ERROR" `
            -LocalPath $LocalPath `
            -S3Uri $S3Uri `
            -LocalFileCount $LocalFileCount `
            -S3FileCount $S3FileCount `
            -Details "Local file count does not match S3 object count."
    }

    if ([int64]$LocalTotalBytes -eq [int64]$S3TotalBytes) {
        Add-ValidationRow `
            -SourceName $SourceName `
            -RunDate $RunDate `
            -CheckName "TOTAL_BYTES_MATCH" `
            -Status "PASS" `
            -Severity "INFO" `
            -LocalPath $LocalPath `
            -S3Uri $S3Uri `
            -LocalSizeBytes ([int64]$LocalTotalBytes) `
            -S3SizeBytes ([int64]$S3TotalBytes) `
            -Details "Local total bytes match S3 total bytes."
    }
    else {
        Add-ValidationRow `
            -SourceName $SourceName `
            -RunDate $RunDate `
            -CheckName "TOTAL_BYTES_MATCH" `
            -Status "FAIL" `
            -Severity "ERROR" `
            -LocalPath $LocalPath `
            -S3Uri $S3Uri `
            -LocalSizeBytes ([int64]$LocalTotalBytes) `
            -S3SizeBytes ([int64]$S3TotalBytes) `
            -Details "Local total bytes do not match S3 total bytes."
    }

    foreach ($Key in $LocalFileMap.Keys) {
        $LocalInfo = $LocalFileMap[$Key]
        $RelativePath = $LocalInfo.RelativePath
        $LocalSize = [int64]$LocalInfo.SizeBytes

        if ($S3ObjectMap.ContainsKey($Key)) {
            $S3Size = [int64]$S3ObjectMap[$Key]

            if ($LocalSize -eq $S3Size) {
                Add-ValidationRow `
                    -SourceName $SourceName `
                    -RunDate $RunDate `
                    -CheckName "FILE_EXISTS_AND_SIZE_MATCH" `
                    -Status "PASS" `
                    -Severity "INFO" `
                    -LocalPath $LocalPath `
                    -S3Uri "s3://$BucketName/$Key" `
                    -FileName $RelativePath `
                    -LocalSizeBytes $LocalSize `
                    -S3SizeBytes $S3Size `
                    -Details "Local file exists in S3 and file size matches."
            }
            else {
                Add-ValidationRow `
                    -SourceName $SourceName `
                    -RunDate $RunDate `
                    -CheckName "FILE_EXISTS_AND_SIZE_MATCH" `
                    -Status "FAIL" `
                    -Severity "ERROR" `
                    -LocalPath $LocalPath `
                    -S3Uri "s3://$BucketName/$Key" `
                    -FileName $RelativePath `
                    -LocalSizeBytes $LocalSize `
                    -S3SizeBytes $S3Size `
                    -Details "Local file exists in S3 but file size does not match."
            }
        }
        else {
            Add-ValidationRow `
                -SourceName $SourceName `
                -RunDate $RunDate `
                -CheckName "FILE_EXISTS_IN_S3" `
                -Status "FAIL" `
                -Severity "ERROR" `
                -LocalPath $LocalPath `
                -S3Uri "s3://$BucketName/$Key" `
                -FileName $RelativePath `
                -LocalSizeBytes $LocalSize `
                -Details "Local file is missing from S3."
        }
    }

    foreach ($Key in $S3ObjectMap.Keys) {
        if (-not $LocalFileMap.ContainsKey($Key)) {
            $RelativePath = $Key.Substring($S3Prefix.Length)

            Add-ValidationRow `
                -SourceName $SourceName `
                -RunDate $RunDate `
                -CheckName "UNEXPECTED_S3_OBJECT" `
                -Status "FAIL" `
                -Severity "WARNING" `
                -LocalPath $LocalPath `
                -S3Uri "s3://$BucketName/$Key" `
                -FileName $RelativePath `
                -S3SizeBytes ([int64]$S3ObjectMap[$Key]) `
                -Details "S3 object exists but no matching local file was found. This may be acceptable if older files were intentionally kept."
        }
    }
}

$Rows | Export-Csv -Path $ReportPath -NoTypeInformation -Encoding UTF8

$ErrorCount = ($Rows | Where-Object { $_.status -eq "FAIL" -and $_.severity -eq "ERROR" }).Count
$WarningCount = ($Rows | Where-Object { $_.status -eq "FAIL" -and $_.severity -eq "WARNING" }).Count
$PassCount = ($Rows | Where-Object { $_.status -eq "PASS" }).Count

Write-Host ""
Write-Host "S3 upload validation report written to:"
Write-Host $ReportPath
Write-Host ""
Write-Host "PASS:    $PassCount"
Write-Host "ERRORS:  $ErrorCount"
Write-Host "WARNINGS:$WarningCount"

if ($ErrorCount -gt 0) {
    throw "S3 upload validation failed with $ErrorCount error-level failure(s)."
}