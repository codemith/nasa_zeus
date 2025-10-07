# 🚀 NASA Zeus AWS Deployment Checklist

**Status**: Ready to Deploy ✅  
**Date**: October 7, 2025  
**Local Testing**: All systems working perfectly

---

## ✅ Pre-Deployment Checklist

### 1. Local Testing Complete
- [x] Docker containers running successfully
- [x] Backend API working (port 8000)
- [x] Frontend working (port 3000)
- [x] Gemini AI service working (port 8001)
- [x] User authentication working
- [x] Data display working (AQI, alerts, reports)
- [x] Database functioning correctly
- [x] All widgets displaying properly

### 2. Required Files Present
- [x] `deployment/docker-compose.yml`
- [x] `deployment/Dockerfile.backend`
- [x] `deployment/Dockerfile.frontend`
- [x] `deployment/Dockerfile.gemini`
- [x] `deployment/nginx.conf`
- [x] `deployment/deploy-aws.sh`
- [x] `.env` file with API keys

### 3. AWS Prerequisites
- [ ] AWS Account created
- [ ] AWS CLI installed and configured
- [ ] Payment method added to AWS account
- [ ] Region selected (recommended: us-east-1)

---

## 🔧 Quick Deployment Steps

### Option A: Automated Deployment (Recommended)

```bash
# 1. Navigate to deployment directory
cd /Users/mithileshbiradar/Desktop/Lockin_Repository/nasa-zeus/nasa-zeus/deployment

# 2. Make deploy script executable
chmod +x deploy-aws.sh

# 3. Run deployment script
./deploy-aws.sh
```

The script will:
1. ✅ Create security group
2. ✅ Create SSH key pair
3. ✅ Launch EC2 instance
4. ✅ Install Docker on instance
5. ✅ Upload your code
6. ✅ Build and start containers
7. ✅ Configure nginx reverse proxy

**Estimated time**: 10-15 minutes

---

### Option B: Manual Deployment (Step by Step)

#### Step 1: Configure AWS CLI
```bash
aws configure
# Enter your credentials:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output format: json
```

#### Step 2: Create .env file
```bash
# Make sure .env is in the root directory
cd /Users/mithileshbiradar/Desktop/Lockin_Repository/nasa-zeus/nasa-zeus

# Check if .env exists
ls -la .env

# If not, create it with:
cat > .env << 'EOF'
OPENWEATHERMAP_API_KEY=your_key_here
OPENAQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
EOF
```

#### Step 3: Run Deployment
```bash
cd deployment
chmod +x deploy-aws.sh
./deploy-aws.sh
```

---

## 🌐 Post-Deployment Access

### After Deployment Success:

1. **Get Public IP Address**:
   ```bash
   aws ec2 describe-instances \
     --filters "Name=tag:Name,Values=nasa-zeus-app" \
     --query 'Reservations[0].Instances[0].PublicIpAddress' \
     --output text
   ```

2. **Access Application**:
   - Frontend: `http://<PUBLIC_IP>`
   - Backend API: `http://<PUBLIC_IP>/api`
   - Gemini AI: `http://<PUBLIC_IP>/gemini`

3. **SSH into Instance** (if needed):
   ```bash
   ssh -i nasa-zeus-key.pem ubuntu@<PUBLIC_IP>
   ```

---

## 📊 Cost Estimate

### Monthly AWS Costs:
| Service | Specs | Cost |
|---------|-------|------|
| EC2 t3.micro | 2 vCPU, 1GB RAM | ~$7-8 |
| EBS Storage | 8GB SSD | ~$1 |
| Data Transfer | ~50GB/month | ~$4 |
| **Total** | | **~$12-15/month** |

### For Production (Recommended):
| Service | Specs | Cost |
|---------|-------|------|
| EC2 t3.small | 2 vCPU, 2GB RAM | ~$15 |
| RDS PostgreSQL | db.t3.micro | ~$15 |
| Load Balancer | ALB | ~$16 |
| CloudFront | CDN | ~$1-5 |
| **Total** | | **~$47-55/month** |

---

## 🔒 Security Setup

### 1. Update Security Group Rules
```bash
# Only allow your IP for SSH (replace YOUR_IP)
aws ec2 revoke-security-group-ingress \
  --group-id <SECURITY_GROUP_ID> \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id <SECURITY_GROUP_ID> \
  --protocol tcp --port 22 --cidr YOUR_IP/32
```

### 2. Enable HTTPS (Optional but Recommended)
```bash
# Install certbot on EC2 instance
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🧪 Testing After Deployment

### 1. Health Checks
```bash
# Check backend health
curl http://<PUBLIC_IP>/api/

# Check Gemini AI health
curl http://<PUBLIC_IP>/gemini/health

# Check frontend
curl http://<PUBLIC_IP>/
```

### 2. Container Status
```bash
ssh -i nasa-zeus-key.pem ubuntu@<PUBLIC_IP>
docker ps
docker logs nasa-zeus-backend
docker logs nasa-zeus-frontend
docker logs nasa-zeus-gemini
```

### 3. Create Test User
```bash
# SSH into instance
ssh -i nasa-zeus-key.pem ubuntu@<PUBLIC_IP>

# Create test user
docker exec nasa-zeus-backend python -c "
from models.database import SessionLocal, User, UserPreferences
from auth.jwt_handler import get_password_hash

db = SessionLocal()
user = User(
    email='admin@nasa-zeus.com',
    name='Admin User',
    password_hash=get_password_hash('admin123')
)
db.add(user)
db.commit()
db.refresh(user)

prefs = UserPreferences(
    user_id=user.id,
    location_lat=40.7128,
    location_lon=-74.0060,
    health_profile='general',
    alert_threshold=3
)
db.add(prefs)
db.commit()
print('✅ Admin user created')
"
```

---

## 🚨 Troubleshooting

### Issue: Deployment script fails
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check if region is correct
aws configure get region

# Check security group exists
aws ec2 describe-security-groups --filters "Name=group-name,Values=nasa-zeus-sg"
```

### Issue: Can't access application
```bash
# Check instance is running
aws ec2 describe-instances --filters "Name=tag:Name,Values=nasa-zeus-app"

# Check security group allows HTTP
aws ec2 describe-security-groups --group-ids <SECURITY_GROUP_ID>

# SSH and check Docker containers
ssh -i nasa-zeus-key.pem ubuntu@<PUBLIC_IP>
docker ps
```

### Issue: Containers not starting
```bash
# Check logs
docker logs nasa-zeus-backend
docker logs nasa-zeus-frontend
docker logs nasa-zeus-gemini

# Restart containers
cd /home/ubuntu/nasa-zeus
docker-compose down
docker-compose up -d
```

---

## 📝 Domain Setup (Optional)

### Using Route 53:

1. **Register Domain** (if you don't have one):
   ```bash
   # Go to AWS Console → Route 53 → Register domain
   # Example: nasa-zeus.com (~$12/year)
   ```

2. **Create Hosted Zone**:
   ```bash
   aws route53 create-hosted-zone \
     --name nasa-zeus.com \
     --caller-reference "$(date +%s)"
   ```

3. **Add A Record**:
   ```bash
   # Get EC2 public IP
   PUBLIC_IP=$(aws ec2 describe-instances \
     --filters "Name=tag:Name,Values=nasa-zeus-app" \
     --query 'Reservations[0].Instances[0].PublicIpAddress' \
     --output text)
   
   # Create A record pointing to EC2 instance
   # (Do this in AWS Console → Route 53 → Hosted Zones)
   ```

4. **Enable SSL**:
   ```bash
   ssh -i nasa-zeus-key.pem ubuntu@<PUBLIC_IP>
   sudo certbot --nginx -d nasa-zeus.com -d www.nasa-zeus.com
   ```

---

## 🎯 Next Steps After Deployment

1. ✅ **Test all features**
   - Login/registration
   - Air quality display
   - Reports generation
   - Gemini AI predictions

2. ✅ **Set up monitoring**
   - CloudWatch logs
   - CloudWatch alarms for high CPU/memory
   - Email notifications

3. ✅ **Backup strategy**
   - Take EBS snapshot daily
   - Export database regularly

4. ✅ **Performance optimization**
   - Enable CloudFront CDN
   - Set up Redis caching
   - Optimize database queries

5. ✅ **Security hardening**
   - Restrict SSH to your IP only
   - Enable AWS WAF
   - Set up VPC with private subnets
   - Rotate JWT secrets regularly

---

## 🆘 Support Resources

- **AWS Documentation**: https://docs.aws.amazon.com/
- **Docker Documentation**: https://docs.docker.com/
- **Project README**: `../README.md`
- **AWS Support**: AWS Console → Support Center

---

**Ready to deploy?** Run:
```bash
cd deployment
./deploy-aws.sh
```

🚀 Good luck with your deployment!
