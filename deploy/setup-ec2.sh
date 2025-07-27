#!/bin/bash
# EC2 Setup Script for Nimbus Bot

set -e

echo "🚀 Setting up Nimbus Bot on EC2..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Git
sudo apt install -y python3 python3-pip git

# Clone repository
cd /home/ubuntu
if [ ! -d "nimbus-v2" ]; then
    git clone https://github.com/yourusername/nimbus-v2.git
fi

cd nimbus-v2

# Install Python dependencies
pip3 install --user -r requirements.txt

# Create .env file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env file with your tokens:"
    echo "   nano .env"
    echo ""
fi

# Setup systemd service
sudo cp deploy/nimbus-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nimbus-bot

# Create data directory
mkdir -p data

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Start the bot: sudo systemctl start nimbus-bot"
echo "3. Check status: sudo systemctl status nimbus-bot"
echo "4. View logs: sudo journalctl -u nimbus-bot -f"