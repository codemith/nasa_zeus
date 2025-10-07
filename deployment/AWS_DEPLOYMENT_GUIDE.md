# NASA Zeus - AWS Deployment Guide

## 📋 Table of Contents
1. [Deployment Architecture](#deployment-architecture)
2. [Prerequisites](#prerequisites)
3. [Option 1: EC2 with Docker (Recommended)](#option-1-ec2-with-docker-recommended)
4. [Option 2: Elastic Beanstalk](#option-2-elastic-beanstalk)
5. [Option 3: ECS/Fargate](#option-3-ecsfargate)
6. [Database Setup (RDS)](#database-setup-rds)
7. [Environment Configuration](#environment-configuration)
8. [Domain & SSL Setup](#domain--ssl-setup)
9. [Monitoring & Logging](#monitoring--logging)
10. [Troubleshooting](#troubleshooting)

---

## 🏗️ Deployment Architecture

### Recommended AWS Architecture:
```
┌─────────────────────────────────────────────────────────────┐
│  CloudFront (CDN) → S3 (Frontend Static Files)              │
│  ↓                                                           │
│  Application Load Balancer                                  │
│  ├─ Target Group 1: Backend (Port 8000) → EC2/ECS          │
│  ├─ Target Group 2: Gemini AI (Port 8001) → EC2/ECS        │
│  └─ RDS PostgreSQL (Private Subnet)                         │
└─────────────────────────────────────────────────────────────┘
```

### Cost Estimate (Monthly):
- EC2 t3.medium (2 vCPU, 4GB RAM): ~$30
- RDS db.t3.micro PostgreSQL: ~$15
- Application Load Balancer: ~$16
- S3 + CloudFront: ~$1-5
- **Total: ~$62-70/month**

---

## 🚀 Prerequisites

### 1. AWS Account Setup
```bash
# Install AWS CLI
brew install awscli  # macOS
# OR
pip install awscli

# Configure AWS credentials
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format: json
```

### 2. Required Tools
```bash
# Docker (for containerization)
brew install docker  # macOS

# Docker Compose
brew install docker-compose

# Verify installations
docker --version
docker-compose --version
aws --version
```

### 3. Domain Name (Optional but Recommended)
- Purchase domain from Route 53 or use existing domain
- Example: `airquality.yourdomain.com`

---

## 🐳 Option 1: EC2 with Docker (Recommended)

### Step 1: Create Dockerfiles

**Backend Dockerfile** (`Dockerfile.backend`):
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY auth/ ./auth/
COPY models/ ./models/
COPY preprocess/ ./preprocess/

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Gemini AI Dockerfile** (`Dockerfile.gemini`):
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY gemini_weather_agent.py .
COPY o3_predictor.py .
COPY MACHINE_LEARNING/ ./MACHINE_LEARNING/
COPY data/ ./data/

EXPOSE 8001

CMD ["python", "gemini_weather_agent.py"]
```

**Frontend Dockerfile** (`Dockerfile.frontend`):
```dockerfile
FROM node:24-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./
RUN npm ci

# Copy source code
COPY frontend/ .

# Build Next.js app
RUN npm run build

# Production image
FROM node:24-alpine

WORKDIR /app

# Copy built files
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]
```

**Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
      - OPENAQ_API_KEY=${OPENAQ_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  gemini:
    build:
      context: .
      dockerfile: Dockerfile.gemini
    ports:
      - "8001:8001"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - backend
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXT_PUBLIC_GEMINI_URL=http://gemini:8001
    depends_on:
      - backend
      - gemini
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
      - gemini
    restart: unless-stopped
```

### Step 2: Launch EC2 Instance

```bash
# 1. Create security group
aws ec2 create-security-group \
  --group-name nasa-zeus-sg \
  --description "Security group for NASA Zeus application" \
  --region us-east-1

# Get the security group ID from output
SECURITY_GROUP_ID="sg-xxxxxxxxx"

# 2. Add inbound rules
aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp --port 22 --cidr 0.0.0.0/0  # SSH
  
aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp --port 80 --cidr 0.0.0.0/0  # HTTP
  
aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp --port 443 --cidr 0.0.0.0/0  # HTTPS

# 3. Create key pair
aws ec2 create-key-pair \
  --key-name nasa-zeus-key \
  --query 'KeyMaterial' \
  --output text > nasa-zeus-key.pem
  
chmod 400 nasa-zeus-key.pem

# 4. Launch EC2 instance (t3.medium recommended)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --count 1 \
  --instance-type t3.medium \
  --key-name nasa-zeus-key \
  --security-group-ids $SECURITY_GROUP_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=nasa-zeus-app}]'
```

### Step 3: Setup EC2 Instance

```bash
# 1. SSH into instance
ssh -i nasa-zeus-key.pem ec2-user@<EC2_PUBLIC_IP>

# 2. Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and log back in for group changes
exit
ssh -i nasa-zeus-key.pem ec2-user@<EC2_PUBLIC_IP>

# 3. Install Git
sudo yum install -y git

# 4. Clone repository
git clone https://github.com/YOUR_USERNAME/nasa-zeus.git
cd nasa-zeus
```

### Step 4: Configure Environment

```bash
# Create .env file
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/nasazeus

# JWT
JWT_SECRET_KEY=your-generated-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
GEMINI_API_KEY=your-gemini-key
OPENWEATHER_API_KEY=your-openweather-key
OPENAQ_API_KEY=your-openaq-key

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_GEMINI_URL=https://api.yourdomain.com/gemini
EOF

# Secure the file
chmod 600 .env
```

### Step 5: Deploy Application

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Test locally
curl http://localhost:8000/api/health
curl http://localhost:3000
```

### Step 6: Setup Nginx Reverse Proxy

**Create `nginx.conf`**:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream gemini {
        server gemini:8001;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Gemini AI API
        location /gemini/ {
            proxy_pass http://gemini;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_cache_bypass $http_upgrade;
        }
    }
}
```

---

## 🗄️ Database Setup (RDS)

### Step 1: Create RDS PostgreSQL Instance

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name nasa-zeus-subnet-group \
  --db-subnet-group-description "Subnet group for NASA Zeus" \
  --subnet-ids subnet-xxxxxx subnet-yyyyyy

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier nasa-zeus-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username nasaadmin \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --db-subnet-group-name nasa-zeus-subnet-group \
  --vpc-security-group-ids $SECURITY_GROUP_ID \
  --backup-retention-period 7 \
  --no-publicly-accessible
```

### Step 2: Update Security Group for RDS

```bash
# Allow EC2 to connect to RDS
aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp \
  --port 5432 \
  --source-group $SECURITY_GROUP_ID
```

### Step 3: Migrate Database

```bash
# On EC2 instance, install PostgreSQL client
sudo yum install -y postgresql15

# Get RDS endpoint
aws rds describe-db-instances \
  --db-instance-identifier nasa-zeus-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text

# Connect and create database
psql -h your-rds-endpoint.amazonaws.com -U nasaadmin -d postgres
CREATE DATABASE nasazeus;
\q

# Update .env with RDS connection string
DATABASE_URL=postgresql://nasaadmin:YOUR_PASSWORD@your-rds-endpoint:5432/nasazeus

# Restart services
docker-compose down
docker-compose up -d
```

---

## 🌐 Domain & SSL Setup

### Option 1: Using AWS Certificate Manager (ACM)

```bash
# 1. Request certificate
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names *.yourdomain.com \
  --validation-method DNS

# 2. Validate domain (add CNAME records to Route 53)

# 3. Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name nasa-zeus-alb \
  --subnets subnet-xxxxxx subnet-yyyyyy \
  --security-groups $SECURITY_GROUP_ID

# 4. Create target groups for backend and frontend
aws elbv2 create-target-group \
  --name nasa-zeus-backend \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxxx \
  --health-check-path /api/health

# 5. Register EC2 instance with target groups
aws elbv2 register-targets \
  --target-group-arn <target-group-arn> \
  --targets Id=<instance-id>

# 6. Create listener with SSL certificate
aws elbv2 create-listener \
  --load-balancer-arn <alb-arn> \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=<acm-cert-arn> \
  --default-actions Type=forward,TargetGroupArn=<target-group-arn>
```

### Option 2: Using Let's Encrypt (Free)

```bash
# On EC2 instance
sudo yum install -y certbot python3-certbot-nginx

# Stop nginx temporarily
docker-compose stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/key.pem
sudo chown ec2-user:ec2-user ./ssl/*

# Restart nginx
docker-compose up -d nginx

# Setup auto-renewal
echo "0 3 * * * certbot renew --quiet && docker-compose restart nginx" | sudo crontab -
```

---

## 📊 Monitoring & Logging

### CloudWatch Setup

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Configure CloudWatch
cat > /opt/aws/amazon-cloudwatch-agent/etc/config.json << 'EOF'
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/home/ec2-user/nasa-zeus/logs/*.log",
            "log_group_name": "/aws/ec2/nasa-zeus",
            "log_stream_name": "{instance_id}/app"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "NasaZeus",
    "metrics_collected": {
      "cpu": {
        "measurement": [{"name": "cpu_usage_idle"}]
      },
      "mem": {
        "measurement": [{"name": "mem_used_percent"}]
      }
    }
  }
}
EOF

# Start CloudWatch agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### Docker Logging

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f gemini
docker-compose logs -f frontend

# Export logs to file
docker-compose logs > deployment.log 2>&1
```

---

## 🔧 Maintenance Commands

```bash
# Update application
cd ~/nasa-zeus
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d

# Backup database
pg_dump -h your-rds-endpoint -U nasaadmin nasazeus > backup_$(date +%Y%m%d).sql

# Restore database
psql -h your-rds-endpoint -U nasaadmin nasazeus < backup_20251006.sql

# Clean up old Docker images
docker system prune -a

# Monitor resources
docker stats

# Restart specific service
docker-compose restart backend
```

---

## 🚨 Troubleshooting

### Common Issues

**1. Docker containers won't start**
```bash
# Check logs
docker-compose logs backend

# Check if ports are available
sudo netstat -tulpn | grep -E ':(8000|8001|3000)'

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**2. Database connection issues**
```bash
# Test RDS connectivity
telnet your-rds-endpoint.amazonaws.com 5432

# Check security group rules
aws ec2 describe-security-groups --group-ids $SECURITY_GROUP_ID

# Verify environment variables
docker-compose exec backend env | grep DATABASE_URL
```

**3. SSL certificate issues**
```bash
# Test certificate
openssl s_client -connect yourdomain.com:443

# Renew Let's Encrypt certificate
sudo certbot renew --force-renewal
docker-compose restart nginx
```

**4. High memory usage**
```bash
# Check container stats
docker stats

# Upgrade instance type
aws ec2 modify-instance-attribute \
  --instance-id i-xxxxxxxxx \
  --instance-type t3.large
```

---

## 📈 Scaling Options

### Vertical Scaling (Upgrade Instance)
```bash
# Stop instance
aws ec2 stop-instances --instance-ids i-xxxxxxxxx

# Change instance type
aws ec2 modify-instance-attribute \
  --instance-id i-xxxxxxxxx \
  --instance-type '{"Value": "t3.large"}'

# Start instance
aws ec2 start-instances --instance-ids i-xxxxxxxxx
```

### Horizontal Scaling (Multiple Instances + Load Balancer)
1. Create AMI from current instance
2. Launch multiple instances from AMI
3. Setup Application Load Balancer
4. Configure Auto Scaling Group

---

## 💰 Cost Optimization

1. **Use Reserved Instances** (up to 72% savings)
2. **Setup CloudWatch billing alarms**
3. **Use S3 for static frontend** (cheaper than EC2)
4. **Enable RDS autoscaling** for storage
5. **Use AWS Cost Explorer** for analysis

---

## ✅ Post-Deployment Checklist

- [ ] All services running: `docker-compose ps`
- [ ] Backend health check: `https://yourdomain.com/api/health`
- [ ] Frontend loading: `https://yourdomain.com`
- [ ] Gemini AI responding: `https://yourdomain.com/gemini/docs`
- [ ] SSL certificate valid: Check browser padlock
- [ ] Database backups configured
- [ ] CloudWatch monitoring active
- [ ] Domain DNS configured correctly
- [ ] API keys in environment variables (not hardcoded)
- [ ] CORS configured for production domain

---

## 📚 Additional Resources

- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Docker Documentation](https://docs.docker.com/)
- [RDS PostgreSQL Guide](https://docs.aws.amazon.com/rds/postgresql/)
- [Let's Encrypt SSL](https://letsencrypt.org/)

---

**Need Help?** Check the [troubleshooting section](#troubleshooting) or review container logs with `docker-compose logs -f`
