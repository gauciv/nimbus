#!/bin/bash

# EC2 Setup Script for Nimbus Bot Docker Deployment

set -e

echo "🚀 Setting up EC2 for Nimbus Bot deployment..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt-get install unzip -y
unzip awscliv2.zip
sudo ./aws/install

# Create project directory
mkdir -p /home/$USER/nimbus-v2
cd /home/$USER/nimbus-v2

# Clone repository (you'll need to set this up)
# git clone https://github.com/yourusername/nimbus-v2.git .

# Create data and logs directories
mkdir -p data logs

# Create environment file template
cat > .env << 'EOF'
DISCORD_TOKEN=your_discord_token_here
GUILD_ID=your_guild_id_here
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
LOG_LEVEL=INFO
EOF

echo "✅ EC2 setup complete!"
echo "📝 Next steps:"
echo "1. Configure AWS credentials: aws configure"
echo "2. Edit .env file with your tokens"
echo "3. Set up ECR repository"
echo "4. Configure GitHub secrets for CI/CD"

# Create ECR repository
echo "🐳 Creating ECR repository..."
aws ecr create-repository --repository-name nimbus-bot --region ap-southeast-1 || echo "Repository might already exist"

echo "🎉 Setup complete! Ready for deployment."