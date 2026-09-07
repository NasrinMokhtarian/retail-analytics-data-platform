param(
    [string]$AwsProfile = "retail-analytics-dev",
    [string]$Region = "eu-central-1",
    [string]$ReadinessRunDate = "2026-06-16"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$ReportDir = Join-Path $ProjectRoot "reports\aws_redshift_readiness\run_date=$ReadinessRunDate"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$ReportPath = Join-Path $ReportDir "redshift_readiness_report.csv"

$Rows = New-Object System.Collections.Generic.List[object]

function Add-CheckResult {
    param(
        [string]$CheckName,
        [string]$Category,
        [string]$Status,
        [string]$Details
    )

    $Rows.Add([PSCustomObject]@{
        readiness_run_date = $ReadinessRunDate
        aws_profile        = $AwsProfile
        aws_region         = $Region
        check_name         = $CheckName
        category           = $Category
        status             = $Status
        details            = $Details
    })
}

function Invoke-ReadinessCommand {
    param(
        [string]$CheckName,
        [string]$Category,
        [scriptblock]$Command
    )

    Write-Host "Checking: $CheckName"

    try {
        $Result = & $Command 2>&1

        Add-CheckResult `
            -CheckName $CheckName `
            -Category $Category `
            -Status "PASS" `
            -Details (($Result | Out-String).Trim())

        Write-Host "  PASS"
    }
    catch {
        Add-CheckResult `
            -CheckName $CheckName `
            -Category $Category `
            -Status "FAIL" `
            -Details $_.Exception.Message

        Write-Host "  FAIL $($_.Exception.Message)"
    }
}

Invoke-ReadinessCommand `
    -CheckName "AWS caller identity" `
    -Category "identity" `
    -Command {
        aws sts get-caller-identity `
            --profile $AwsProfile `
            --region $Region `
            --output json
    }

Invoke-ReadinessCommand `
    -CheckName "Redshift Serverless list namespaces" `
    -Category "redshift-serverless-read" `
    -Command {
        aws redshift-serverless list-namespaces `
            --profile $AwsProfile `
            --region $Region `
            --output json
    }

Invoke-ReadinessCommand `
    -CheckName "Redshift Serverless list workgroups" `
    -Category "redshift-serverless-read" `
    -Command {
        aws redshift-serverless list-workgroups `
            --profile $AwsProfile `
            --region $Region `
            --output json
    }

Invoke-ReadinessCommand `
    -CheckName "Default VPC lookup" `
    -Category "network-read" `
    -Command {
        aws ec2 describe-vpcs `
            --filters "Name=is-default,Values=true" `
            --profile $AwsProfile `
            --region $Region `
            --query "Vpcs[].VpcId" `
            --output json
    }

Invoke-ReadinessCommand `
    -CheckName "Subnet lookup" `
    -Category "network-read" `
    -Command {
        aws ec2 describe-subnets `
            --profile $AwsProfile `
            --region $Region `
            --query "Subnets[].SubnetId" `
            --output json
    }

Invoke-ReadinessCommand `
    -CheckName "Security group lookup" `
    -Category "network-read" `
    -Command {
        aws ec2 describe-security-groups `
            --profile $AwsProfile `
            --region $Region `
            --query "SecurityGroups[].GroupId" `
            --output json
    }

Invoke-ReadinessCommand `
    -CheckName "Secrets Manager read readiness" `
    -Category "secrets-read" `
    -Command {
        aws secretsmanager list-secrets `
            --max-results 1 `
            --profile $AwsProfile `
            --region $Region `
            --output json
    }

Invoke-ReadinessCommand `
    -CheckName "IAM role read readiness" `
    -Category "iam-read" `
    -Command {
        aws iam get-user `
            --user-name "terraform-retail-analytics-dev" `
            --profile $AwsProfile `
            --region $Region `
            --output json
    }

$Rows | Export-Csv -Path $ReportPath -NoTypeInformation -Encoding UTF8

$PassCount = ($Rows | Where-Object { $_.status -eq "PASS" }).Count
$FailCount = ($Rows | Where-Object { $_.status -eq "FAIL" }).Count

Write-Host ""
Write-Host "Redshift readiness report written to:"
Write-Host $ReportPath
Write-Host ""
Write-Host "PASS: $PassCount"
Write-Host "FAIL: $FailCount"

if ($FailCount -gt 0) {
    Write-Host ""
    Write-Host "Some readiness checks failed. This does not create cost, but permissions/network setup may need adjustment before Redshift is enabled."
}