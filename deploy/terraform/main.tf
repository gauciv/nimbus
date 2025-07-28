terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-southeast-1" # Singapore
}

# ECR Repository
resource "aws_ecr_repository" "nimbus_bot" {
  name                 = "nimbus-bot"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Security Group
resource "aws_security_group" "nimbus_bot" {
  name_prefix = "nimbus-bot-"
  description = "Security group for Nimbus Bot EC2"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAM Role for EC2
resource "aws_iam_role" "nimbus_bot_role" {
  name = "nimbus-bot-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "nimbus_bot_policy" {
  name = "nimbus-bot-policy"
  role = aws_iam_role.nimbus_bot_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "nimbus_bot_profile" {
  name = "nimbus-bot-profile"
  role = aws_iam_role.nimbus_bot_role.name
}

# EC2 Instance
resource "aws_instance" "nimbus_bot" {
  ami                    = "ami-0497a974f8d5dcef8" # Ubuntu 22.04 LTS in Singapore
  instance_type          = "t3.micro"
  key_name              = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.nimbus_bot.id]
  iam_instance_profile   = aws_iam_instance_profile.nimbus_bot_profile.name

  user_data = file("${path.module}/user-data.sh")

  tags = {
    Name = "nimbus-bot"
  }
}

# Outputs
output "instance_public_ip" {
  value = aws_instance.nimbus_bot.public_ip
}

output "ecr_repository_url" {
  value = aws_ecr_repository.nimbus_bot.repository_url
}