#!/bin/bash

set -e

echo "🚀 Setting up Nimbus Bot on AWS EC2 (FREE TIER)"

# 1. Create key pair
echo "🔑 Creating SSH key pair..."
aws ec2 create-key-pair --key-name nimbus-key --query 'KeyMaterial' --output text > nimbus-key.pem
chmod 400 nimbus-key.pem

# 2. Deploy EC2 instance
echo "📦 Creating EC2 instance..."
aws cloudformation deploy \
    --template-file ec2.yml \
    --stack-name nimbus-bot \
    --capabilities CAPABILITY_IAM

# 3. Get instance IP
INSTANCE_IP=$(aws cloudformation describe-stacks \
    --stack-name nimbus-bot \
    --query 'Stacks[0].Outputs[?OutputKey==`InstanceIP`].OutputValue' \
    --output text)

echo "✅ Instance created: $INSTANCE_IP"
echo ""
echo "📋 Setup GitHub secrets:"
echo "EC2_HOST: $INSTANCE_IP"
echo "EC2_SSH_KEY: $(cat nimbus-key.pem)"
echo ""
echo "🔧 SSH into instance and run:"
echo "ssh -i nimbus-key.pem ec2-user@$INSTANCE_IP"
echo "git clone https://github.com/YOUR_USERNAME/nimbus-v2.git"
echo "cd nimbus-v2 && cp .env.example .env && nano .env"
echo "docker-compose up -d"