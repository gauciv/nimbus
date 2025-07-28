#!/bin/bash

set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
apt-get install unzip -y
unzip awscliv2.zip
./aws/install

# Install Git
apt-get install git -y

# Create project directory
mkdir -p /home/ubuntu/nimbus-v2
cd /home/ubuntu/nimbus-v2

# Clone repository
git clone https://github.com/yourusername/nimbus-v2.git .

# Create data and logs directories
mkdir -p data logs
chown -R ubuntu:ubuntu /home/ubuntu/nimbus-v2

# Create environment file
cat > .env << 'EOF'
DISCORD_TOKEN=${discord_token}
GUILD_ID=${guild_id}
GROQ_API_KEY=${groq_api_key}
HUGGINGFACE_API_KEY=${huggingface_api_key}
LOG_LEVEL=INFO
EOF

# Set proper permissions
chown ubuntu:ubuntu .env
chmod 600 .env

# Configure AWS CLI for ubuntu user
sudo -u ubuntu aws configure set region ap-southeast-1

# Login to ECR and start the bot
sudo -u ubuntu bash << 'USEREOF'
cd /home/ubuntu/nimbus-v2
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin ${ecr_repository_uri}
docker-compose -f docker-compose.prod.yml up -d
USEREOF

echo "✅ Nimbus Bot setup complete!"