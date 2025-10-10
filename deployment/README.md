# NASA Zeus Deployment Files

This directory contains all files needed to deploy NASA Zeus to various platforms.

## 📁 Directory Contents

### Docker Configuration
- **`Dockerfile.backend`** - FastAPI backend container
- **`Dockerfile.frontend`** - Next.js frontend container  
- **`Dockerfile.gemini`** - Gemini AI agent container
- **`docker-compose.yml`** - Production orchestration (optimized for t3.micro)
- **`docker-compose.minimal.yml`** - Minimal configuration
- **`.dockerignore`** - Files to exclude from Docker builds
- **`nginx.conf`** - Nginx reverse proxy configuration

### AWS Deployment (Docker-based)
- **`deploy-aws.sh`** - Automated AWS EC2 deployment script with Docker
- **`AWS_DEPLOYMENT_GUIDE.md`** - Comprehensive deployment guide (520 lines)
- **`COST_OPTIMIZATION.md`** - Cost analysis and optimization details
- **`setup-ec2-complete.sh`** - Complete EC2 setup script

### AWS Deployment (Non-Docker - Production Domain) ⭐ NEW
- **`deploy-nasazeus-org.sh`** - Complete deployment script for nasazeus.org (t3.small)
- **`DEPLOY_NASAZEUS_ORG.md`** - Full deployment guide with troubleshooting
- **`QUICKSTART_DEPLOY.md`** - Quick reference for nasazeus.org deployment
- **`DEPLOYMENT_CHECKLIST.md`** - Pre and post-deployment checklist

## 🚀 Quick Start

### Prerequisites
1. AWS CLI configured: `aws configure`
2. Docker installed locally (for testing)
3. Environment variables configured in root `.env` file

### Deploy to AWS (Recommended)

```bash
cd deployment
./deploy-aws.sh
```

**Cost**: ~$10.49/month (or FREE with AWS Free Tier for 12 months)

**What it does**:
- Creates EC2 t3.micro instance (1GB RAM, 2 vCPU)
- Installs Docker on the instance
- Deploys 4 containers: Backend, Frontend, Gemini AI, Nginx
- Configures security groups (ports 80, 443, 22)
- Provides public URL for access

## 🚀 Quick Start

### Option 1: Production Domain Deployment (nasazeus.org) ⭐ RECOMMENDED

**Best for**: Production deployment with custom domain and SSL

```bash
cd deployment

# Phase 1: Setup AWS infrastructure (local machine)
./deploy-nasazeus-org.sh aws-setup

# Phase 2: Setup server (on EC2 instance after SSH)
./deploy-nasazeus-org.sh server-setup
```

**Features**:
- Custom domain with automatic SSL (Let's Encrypt)
- No Docker overhead - native PM2 process management
- Caddy reverse proxy with auto-HTTPS
- EC2 t3.small (2GB RAM, 2 vCPU)
- Cost: ~$15/month

📖 **See**: [QUICKSTART_DEPLOY.md](./QUICKSTART_DEPLOY.md) for 5-minute guide  
📖 **See**: [DEPLOY_NASAZEUS_ORG.md](./DEPLOY_NASAZEUS_ORG.md) for full documentation  
📋 **See**: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) for checklist

---

### Option 2: Docker-based AWS Deployment

**Best for**: Quick testing, containerized deployment

```bash
cd deployment
./deploy-aws.sh
```

**Cost**: ~$10.49/month (or FREE with AWS Free Tier for 12 months)

**What it does**:
- Creates EC2 t3.micro instance (1GB RAM, 2 vCPU)
- Installs Docker on the instance
- Deploys 4 containers: Backend, Frontend, Gemini AI, Nginx
- Configures security groups (ports 80, 443, 22)
- Provides public URL for access

**Duration**: ~10-15 minutes

### Local Testing with Docker

```bash
cd deployment
docker-compose up --build
```

Access at: http://localhost

## 📊 System Requirements

### Production (AWS t3.micro)
- **Memory**: 1GB total
  - Backend: 256MB
  - Frontend: 256MB
  - Gemini AI: 256MB
  - Nginx: 64MB
- **CPU**: 2 vCPU
- **Storage**: 8GB EBS volume
- **Capacity**: 50 concurrent users, 1000 req/hour

### Development
- Docker Desktop with 2GB+ RAM
- 10GB free disk space

## 📖 Documentation

- **[AWS Deployment Guide](./AWS_DEPLOYMENT_GUIDE.md)** - Full deployment instructions with 3 options (EC2, Elastic Beanstalk, ECS)
- **[Cost Optimization](./COST_OPTIMIZATION.md)** - Detailed cost breakdown, capacity analysis, scaling guidance

## 🔐 Security Notes

1. **Environment Variables**: Never commit `.env` file (already in .gitignore)
2. **API Keys**: Store in `.env`, mounted to containers via docker-compose
3. **AWS Credentials**: Use IAM user with minimum required permissions:
   - AmazonEC2FullAccess
   - AmazonVPCFullAccess
   - IAMReadOnlyAccess

## 🛠️ Customization

### Change AWS Region
Edit `deploy-aws.sh`, line 19:
```bash
REGION="us-west-2"  # Change from us-east-1
```

### Increase Resources
Edit `docker-compose.yml` memory limits:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M  # Double the memory
```

### Add Domain/SSL
See [AWS Deployment Guide](./AWS_DEPLOYMENT_GUIDE.md) Section 6: SSL/TLS Setup

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify AWS credentials: `aws sts get-caller-identity`
3. Review [AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md) troubleshooting section

## 🎯 Architecture

```
User → Nginx (Port 80/443)
         ├─→ Frontend (Next.js) → Port 3000
         ├─→ Backend (FastAPI) → Port 8000
         └─→ Gemini AI → Port 8001

Data Flow:
Frontend → Backend API → OpenAQ/OpenWeatherMap APIs
                      → Gemini AI Agent → NASA TEMPO data
```

## 📝 Version History

- **v1.0** - Initial deployment configuration (October 2025)
  - Optimized for minimal cost ($10.49/month)
  - t3.micro instance with Docker Compose
  - 86% cost reduction from original setup
