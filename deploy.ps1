<#
.SYNOPSIS
    Content DNA OS – Full AWS Deployment Script (Lambda + S3 + CloudFront)

.DESCRIPTION
    Deploys the backend to AWS Lambda via SAM, builds the frontend,
    uploads it to S3, and invalidates CloudFront cache.

.PREREQUISITES
    1. AWS CLI v2 installed and configured:  aws configure
    2. AWS SAM CLI installed:                winget install Amazon.SAM-CLI
    3. Node.js 18+ installed:                winget install OpenJS.NodeJS.LTS
    4. Python 3.12 installed
    5. AWS credentials with permissions for Lambda, API Gateway, DynamoDB, 
       S3, CloudFront, IAM, Bedrock

.USAGE
    .\deploy.ps1                  # Full deploy (backend + frontend)
    .\deploy.ps1 -BackendOnly     # Deploy only Lambda backend
    .\deploy.ps1 -FrontendOnly    # Deploy only frontend to S3/CloudFront
#>

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [string]$Region = "us-east-1",
    [string]$StackName = "content-dna-os"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# If run from project root directly
if (-not (Test-Path "$ProjectRoot\infrastructure\template.yaml")) {
    $ProjectRoot = Get-Location
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Content DNA OS - AWS Deployment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Stack:   $StackName" -ForegroundColor Gray
Write-Host "  Region:  $Region" -ForegroundColor Gray
Write-Host "  Root:    $ProjectRoot" -ForegroundColor Gray
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# ──── Step 0: Verify Prerequisites ─────────────────────────────────────────
function Test-Prerequisites {
    Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow

    $missing = @()
    if (-not (Get-Command "aws" -ErrorAction SilentlyContinue)) { $missing += "AWS CLI (aws)" }
    if (-not (Get-Command "sam" -ErrorAction SilentlyContinue)) { $missing += "AWS SAM CLI (sam)" }
    if (-not (Get-Command "node" -ErrorAction SilentlyContinue)) { $missing += "Node.js (node)" }
    if (-not (Get-Command "npm" -ErrorAction SilentlyContinue)) { $missing += "npm" }
    if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) { $missing += "Python (python)" }

    if ($missing.Count -gt 0) {
        Write-Host "  MISSING:" -ForegroundColor Red
        foreach ($m in $missing) {
            Write-Host "    - $m" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "  Install them first:" -ForegroundColor Yellow
        Write-Host "    winget install Amazon.AWSCLI" -ForegroundColor Gray
        Write-Host "    winget install Amazon.SAM-CLI" -ForegroundColor Gray
        Write-Host "    winget install OpenJS.NodeJS.LTS" -ForegroundColor Gray
        Write-Host "    winget install Python.Python.3.12" -ForegroundColor Gray
        throw "Missing prerequisites"
    }

    # Verify AWS credentials
    try {
        $identity = aws sts get-caller-identity --output json 2>&1 | ConvertFrom-Json
        Write-Host "  AWS Account: $($identity.Account)" -ForegroundColor Green
        Write-Host "  AWS User:    $($identity.Arn)" -ForegroundColor Green
    } catch {
        Write-Host "  AWS credentials not configured!" -ForegroundColor Red
        Write-Host "  Run: aws configure" -ForegroundColor Yellow
        throw "AWS credentials not configured"
    }

    Write-Host "  All prerequisites OK" -ForegroundColor Green
    Write-Host ""
}

# ──── Step 1: Create SAM deployment bucket ──────────────────────────────────
function New-DeployBucket {
    $accountId = (aws sts get-caller-identity --query Account --output text).Trim()
    $script:DeployBucket = "content-dna-deploy-$accountId"

    Write-Host "[2/6] Ensuring deploy bucket: $script:DeployBucket" -ForegroundColor Yellow
    aws s3 mb "s3://$script:DeployBucket" --region $Region 2>$null
    Write-Host "  Bucket ready" -ForegroundColor Green
    Write-Host ""
}

# ──── Step 2: SAM Build & Deploy (Backend) ──────────────────────────────────
function Deploy-Backend {
    Write-Host "[3/6] Building backend with SAM..." -ForegroundColor Yellow
    Push-Location $ProjectRoot

    sam build --template infrastructure/template.yaml --build-dir .aws-sam/build

    Write-Host ""
    Write-Host "[4/6] Deploying backend to AWS Lambda..." -ForegroundColor Yellow

    sam deploy `
        --template-file .aws-sam/build/template.yaml `
        --stack-name $StackName `
        --capabilities CAPABILITY_IAM `
        --region $Region `
        --s3-bucket $script:DeployBucket `
        --no-fail-on-empty-changeset `
        --no-confirm-changeset

    Pop-Location
    Write-Host "  Backend deployed!" -ForegroundColor Green
    Write-Host ""
}

# ──── Step 3: Get Stack Outputs ─────────────────────────────────────────────
function Get-StackOutputs {
    $outputs = aws cloudformation describe-stacks `
        --stack-name $StackName `
        --region $Region `
        --query "Stacks[0].Outputs" `
        --output json 2>&1 | ConvertFrom-Json

    $script:Outputs = @{}
    foreach ($o in $outputs) {
        $script:Outputs[$o.OutputKey] = $o.OutputValue
    }

    Write-Host "  Stack Outputs:" -ForegroundColor Cyan
    foreach ($key in $script:Outputs.Keys) {
        Write-Host "    $key = $($script:Outputs[$key])" -ForegroundColor Gray
    }
    Write-Host ""
}

# ──── Step 4: Build & Deploy Frontend ───────────────────────────────────────
function Deploy-Frontend {
    Write-Host "[5/6] Building frontend..." -ForegroundColor Yellow

    $apiUrl = $script:Outputs["ApiUrl"]
    $frontendBucket = $script:Outputs["FrontendBucket"]
    $cfDistId = $script:Outputs["CloudFrontDistributionId"]
    $frontendUrl = $script:Outputs["FrontendUrl"]

    if (-not $frontendBucket) {
        Write-Host "  No FrontendBucket output found. Deploy backend first." -ForegroundColor Red
        return
    }

    Push-Location "$ProjectRoot\frontend"

    # Install deps if needed
    if (-not (Test-Path "node_modules")) {
        Write-Host "  Installing npm dependencies..." -ForegroundColor Gray
        npm install
    }

    # Build with the API URL pointing to CloudFront (which proxies /api to Lambda)
    # Since CloudFront handles both frontend and API, use relative /api path
    $env:VITE_API_BASE = "/api"
    npm run build
    Remove-Item Env:\VITE_API_BASE -ErrorAction SilentlyContinue

    Write-Host ""
    Write-Host "[6/6] Uploading frontend to S3..." -ForegroundColor Yellow

    # Sync built files to S3
    aws s3 sync dist "s3://$frontendBucket" `
        --region $Region `
        --delete

    # Set correct content types for key files
    aws s3 cp "s3://$frontendBucket" "s3://$frontendBucket" `
        --recursive `
        --exclude "*" `
        --include "*.js" `
        --content-type "application/javascript" `
        --metadata-directive REPLACE `
        --region $Region

    aws s3 cp "s3://$frontendBucket" "s3://$frontendBucket" `
        --recursive `
        --exclude "*" `
        --include "*.css" `
        --content-type "text/css" `
        --metadata-directive REPLACE `
        --region $Region

    # Invalidate CloudFront cache
    if ($cfDistId) {
        Write-Host "  Invalidating CloudFront cache..." -ForegroundColor Gray
        aws cloudfront create-invalidation `
            --distribution-id $cfDistId `
            --paths "/*" `
            --region $Region | Out-Null
    }

    Pop-Location

    Write-Host "  Frontend deployed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Frontend:  $frontendUrl" -ForegroundColor Cyan
    Write-Host "  API:       $apiUrl" -ForegroundColor Cyan
    Write-Host "  API Docs:  $($apiUrl)docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  The frontend uses CloudFront which proxies" -ForegroundColor Gray
    Write-Host "  /api/* requests to your Lambda backend." -ForegroundColor Gray
    Write-Host ""
    Write-Host "  NOTE: CloudFront may take 5-10 minutes to" -ForegroundColor Yellow
    Write-Host "  fully propagate after first deploy." -ForegroundColor Yellow
    Write-Host "==================================================" -ForegroundColor Green
}

# ──── Main ──────────────────────────────────────────────────────────────────
try {
    Test-Prerequisites
    New-DeployBucket

    if (-not $FrontendOnly) {
        Deploy-Backend
    }

    Get-StackOutputs

    if (-not $BackendOnly) {
        Deploy-Frontend
    } else {
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host "  BACKEND DEPLOYMENT COMPLETE!" -ForegroundColor Green
        Write-Host "==================================================" -ForegroundColor Green
        Write-Host "  API: $($script:Outputs['ApiUrl'])" -ForegroundColor Cyan
        Write-Host "==================================================" -ForegroundColor Green
    }
} catch {
    Write-Host ""
    Write-Host "DEPLOYMENT FAILED: $_" -ForegroundColor Red
    Write-Host ""
    exit 1
}
