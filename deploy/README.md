# Nimbus Bot Docker Deployment Guide

## Quick Setup

### 1. EC2 Instance Setup
```bash
# Run on your EC2 instance
curl -fsSL https://raw.githubusercontent.com/yourusername/nimbus-v2/main/deploy/setup-ec2.sh | bash
```

### 2. GitHub Secrets Configuration
Add these secrets to your GitHub repository:

```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
EC2_HOST=your_ec2_public_ip
EC2_USER=ubuntu
EC2_SSH_KEY=your_private_key_content
DISCORD_TOKEN=your_discord_token
GROQ_API_KEY=your_groq_key
HUGGINGFACE_API_KEY=your_hf_key
```

### 3. Environment Variables on EC2
Edit `/home/ubuntu/nimbus-v2/.env`:
```bash
DISCORD_TOKEN=your_discord_token_here
GUILD_ID=your_guild_id_here
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
LOG_LEVEL=INFO
```

## Deployment Process

1. **Push to main branch** → Triggers CI/CD
2. **Docker image built** → Pushed to ECR
3. **Zero-downtime deployment** → Rolling update on EC2
4. **Health checks** → Ensures bot is running

## Commands

```bash
# Check bot status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f nimbus-bot

# Manual restart
docker-compose -f docker-compose.prod.yml restart nimbus-bot

# Update manually
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring

- **Health Check**: Bot container has built-in health checks
- **Logs**: Centralized logging with rotation
- **Auto-restart**: Container restarts on failure
- **Resource Limits**: Configurable in docker-compose

## Zero Downtime Updates

The CI/CD pipeline ensures:
1. New image is built and tested
2. Old container keeps running during deployment
3. New container starts with health checks
4. Traffic switches only after health check passes
5. Old container is gracefully stopped