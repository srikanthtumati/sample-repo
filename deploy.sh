#!/bin/bash

echo "🚀 Deploying Events API..."

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt -t .
cd ..

# Install CDK dependencies
echo "📦 Installing CDK dependencies..."
cd infrastructure
pip install -r requirements.txt

# Bootstrap CDK (only needed once per account/region)
echo "🔧 Bootstrapping CDK..."
cdk bootstrap

# Deploy the stack
echo "🚀 Deploying stack..."
cdk deploy --require-approval never

echo "✅ Deployment complete!"
