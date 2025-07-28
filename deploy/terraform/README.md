# Automated EC2 Deployment with Terraform

## One-Command Setup

No SSH required! Everything is automated.

### 1. Prerequisites
- AWS CLI configured
- Terraform installed
- AWS key pair created in Singapore region

### 2. Deploy
```bash
cd deploy/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

terraform init
terraform plan
terraform apply
```

### 3. Done!
- EC2 instance created in Singapore
- Docker and dependencies installed automatically
- Bot starts running immediately
- ECR repository created
- CI/CD ready

## What Gets Created
- **EC2 t3.micro** in ap-southeast-1 (Singapore)
- **ECR repository** for Docker images
- **Security groups** with proper ports
- **IAM roles** for ECR access
- **Automated setup** via user data

## GitHub Secrets Needed
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-southeast-1
EC2_HOST=<terraform_output_ip>
EC2_USER=ubuntu
EC2_SSH_KEY=your_private_key
```

## Commands
```bash
# Get instance IP
terraform output instance_public_ip

# Get ECR URL
terraform output ecr_repository_url

# Destroy everything
terraform destroy
```