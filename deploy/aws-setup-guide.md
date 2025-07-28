# AWS Setup Guide for Nimbus Bot

## 1. Key Pair Setup

### Create EC2 Key Pair in Singapore Region
```bash
# Via AWS CLI
aws ec2 create-key-pair --key-name nimbus-bot-key --region ap-southeast-1 --query 'KeyMaterial' --output text > nimbus-bot-key.pem
chmod 400 nimbus-bot-key.pem
```

**Or via AWS Console:**
1. Go to EC2 → Key Pairs (Singapore region)
2. Create Key Pair → Name: `nimbus-bot-key`
3. Download the `.pem` file
4. Keep it secure - you'll need it for GitHub secrets

## 2. IAM User for GitHub Actions

### Create IAM User (Recommended)
**Don't use roles - use a dedicated user for CI/CD**

1. **Create User:**
   - Name: `nimbus-bot-cicd`
   - Access type: Programmatic access only

2. **Required Permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchDeleteImage",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances"
            ],
            "Resource": "*"
        }
    ]
}
```

3. **Save Credentials:**
   - Access Key ID
   - Secret Access Key

## 3. IAM User for Terraform (Your Local Machine)

### Create Terraform User
**Name:** `nimbus-bot-terraform`

**Permissions:** Attach these managed policies:
- `AmazonEC2FullAccess`
- `AmazonECRFullAccess` 
- `IAMFullAccess`

**Or create custom policy:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "ecr:*",
                "iam:*"
            ],
            "Resource": "*"
        }
    ]
}
```

## 4. GitHub Secrets Configuration

```
AWS_ACCESS_KEY_ID=<cicd-user-access-key>
AWS_SECRET_ACCESS_KEY=<cicd-user-secret-key>
AWS_REGION=ap-southeast-1
EC2_HOST=<will-get-from-terraform-output>
EC2_USER=ubuntu
EC2_SSH_KEY=<content-of-nimbus-bot-key.pem>
```

## 5. Local AWS Configuration

```bash
# Configure AWS CLI with Terraform user credentials
aws configure --profile nimbus-terraform
# Enter Terraform user's access key and secret
# Region: ap-southeast-1

# Use the profile
export AWS_PROFILE=nimbus-terraform
```

## Summary

- **Key Pair:** `nimbus-bot-key` (for EC2 SSH access)
- **CI/CD User:** `nimbus-bot-cicd` (for GitHub Actions)
- **Terraform User:** `nimbus-bot-terraform` (for your local Terraform)
- **Region:** `ap-southeast-1` (Singapore)