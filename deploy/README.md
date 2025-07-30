# Deployment Guide

## AWS EC2 Free Tier Deployment

### Prerequisites
- AWS CLI configured
- GitHub repository set up

### Deploy
```bash
cd deploy
./setup.sh
```

### GitHub Secrets
Add these to your GitHub repo secrets:
- `EC2_HOST`: Instance IP from setup output
- `EC2_SSH_KEY`: Private key from setup output

### Manual Setup on EC2
```bash
ssh -i nimbus-key.pem ec2-user@YOUR_IP
git clone https://github.com/YOUR_USERNAME/nimbus-v2.git
cd nimbus-v2
cp .env.example .env
nano .env  # Add your tokens
docker-compose up -d
```

### Auto-Deploy
Push to `main` branch triggers automatic deployment via GitHub Actions.