#!/bin/bash
# Content DNA OS – AWS SAM Deployment Script

set -e

STACK_NAME="content-dna-os"
REGION="${AWS_REGION:-us-east-1}"
S3_BUCKET="${SAM_BUCKET:-content-dna-deploy-$(aws sts get-caller-identity --query Account --output text)}"

echo "🧬 Content DNA OS – Deploying to AWS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stack:  $STACK_NAME"
echo "Region: $REGION"
echo "Bucket: $S3_BUCKET"
echo ""

# Create deployment bucket if it doesn't exist
aws s3 mb "s3://$S3_BUCKET" --region "$REGION" 2>/dev/null || true

# Build
echo "📦 Building..."
sam build --template infrastructure/template.yaml

# Package
echo "📤 Packaging..."
sam package \
  --output-template-file packaged.yaml \
  --s3-bucket "$S3_BUCKET" \
  --region "$REGION"

# Deploy
echo "🚀 Deploying..."
sam deploy \
  --template-file packaged.yaml \
  --stack-name "$STACK_NAME" \
  --capabilities CAPABILITY_IAM \
  --region "$REGION" \
  --no-fail-on-empty-changeset

# Get outputs
echo ""
echo "✅ Deployment complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs' \
  --output table \
  --region "$REGION"
