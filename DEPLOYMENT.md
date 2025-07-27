# Nimbus Bot Deployment Guide

## Quick EC2 Setup

### 1. Initial Setup
```bash
# On your EC2 instance
wget https://raw.githubusercontent.com/yourusername/nimbus-v2/main/deploy/setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh
```

### 2. Configure Environment
```bash
cd nimbus-v2
nano .env
```

Add your tokens:
```env
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_guild_id_here
LOG_LEVEL=INFO
HUGGINGFACE_API_KEY=your_hf_key_here
```

### 3. Start the Bot
```bash
sudo systemctl start nimbus-bot
sudo systemctl status nimbus-bot
```

## CI/CD Setup

### GitHub Secrets Required:
- `DISCORD_TOKEN` - Your Discord bot token
- `HUGGINGFACE_API_KEY` - Your Hugging Face API key
- `EC2_HOST` - Your EC2 instance IP
- `EC2_USER` - EC2 username (usually 'ubuntu')
- `EC2_SSH_KEY` - Your private SSH key for EC2

### Automatic Deployment:
- Push to `main` branch triggers deployment
- Zero downtime with systemd service restart
- Health checks ensure successful deployment

## Monitoring

### Health Check Endpoints:
- `http://your-ec2-ip:8001/health` - Basic health status
- `http://your-ec2-ip:8001/status` - Detailed bot status

### View Logs:
```bash
# Real-time logs
sudo journalctl -u nimbus-bot -f

# Recent logs
sudo journalctl -u nimbus-bot --since "1 hour ago"
```

### Service Management:
```bash
# Start/stop/restart
sudo systemctl start nimbus-bot
sudo systemctl stop nimbus-bot
sudo systemctl restart nimbus-bot

# Enable/disable auto-start
sudo systemctl enable nimbus-bot
sudo systemctl disable nimbus-bot
```

## Troubleshooting

### Bot Not Starting:
1. Check logs: `sudo journalctl -u nimbus-bot -n 50`
2. Verify .env file: `cat .env`
3. Test manually: `cd /home/ubuntu/nimbus-v2 && python run_bot.py`

### Deployment Failing:
1. Check GitHub Actions logs
2. Verify SSH key permissions
3. Ensure EC2 security group allows SSH (port 22)

### Health Check Failing:
1. Check if port 8001 is open in security group
2. Verify bot is running: `sudo systemctl status nimbus-bot`
3. Test locally: `curl localhost:8001/health`