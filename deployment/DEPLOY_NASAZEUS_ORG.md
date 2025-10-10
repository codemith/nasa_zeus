# NASA ZEUS Deployment to nasazeus.org

Complete guide for deploying NASA ZEUS to AWS EC2 with custom domain and SSL.

## 📋 Prerequisites

### Local Machine Requirements
- AWS CLI installed and configured (`aws configure`)
- EC2 key pair created (named `nasa-zeus-key`)
- Access to domain registrar for DNS configuration

### AWS Resources Needed
- AWS account with EC2 access
- EC2 key pair (`.pem` file)
- Domain: `nasazeus.org` (with DNS management access)

### API Keys Required
- OpenWeatherMap API key
- OpenAQ API key (optional but recommended)
- Google Gemini API key

## 🚀 Deployment Overview

This deployment uses:
- **EC2 Instance**: t3.small (2 vCPU, 2 GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Next.js 15 (production build)
- **Process Manager**: PM2
- **Reverse Proxy**: Caddy (automatic HTTPS/SSL)
- **Domain**: nasazeus.org

## 📝 Deployment Steps

### Phase 1: AWS Infrastructure Setup (Local Machine)

1. **Prepare the deployment script:**
   ```bash
   cd deployment
   chmod +x deploy-nasazeus-org.sh
   ```

2. **Configure AWS settings in script** (if needed):
   Edit the script and update these variables:
   ```bash
   KEY_PAIR_NAME="nasa-zeus-key"      # Your EC2 key pair name
   AMI_ID="ami-0c7217cdde317cfec"     # Ubuntu 22.04 AMI for your region
   ```

3. **Run AWS infrastructure setup:**
   ```bash
   ./deploy-nasazeus-org.sh aws-setup
   ```

   This will:
   - ✅ Create security group (SSH, HTTP, HTTPS)
   - ✅ Launch EC2 t3.small instance
   - ✅ Output public IP address
   - ✅ Save instance details

4. **Configure DNS:**
   - Log in to your domain registrar
   - Create an A record for `nasazeus.org` → `[EC2_PUBLIC_IP]`
   - Create an A record for `www.nasazeus.org` → `[EC2_PUBLIC_IP]`
   - Wait 5-60 minutes for DNS propagation

5. **Verify DNS propagation:**
   ```bash
   dig nasazeus.org
   nslookup nasazeus.org
   ```

### Phase 2: Server Setup (EC2 Instance)

1. **Copy script to EC2:**
   ```bash
   scp -i nasa-zeus-key.pem deploy-nasazeus-org.sh ubuntu@[EC2_PUBLIC_IP]:~/
   ```

2. **SSH into EC2 instance:**
   ```bash
   ssh -i nasa-zeus-key.pem ubuntu@[EC2_PUBLIC_IP]
   ```

3. **Run server setup:**
   ```bash
   chmod +x deploy-nasazeus-org.sh
   ./deploy-nasazeus-org.sh server-setup
   ```

   This will:
   - ✅ Update system packages
   - ✅ Install Python 3, Node.js 18, PM2, Caddy
   - ✅ Clone NASA ZEUS repository
   - ✅ Setup backend with virtual environment
   - ✅ Install all Python dependencies
   - ✅ Build Next.js frontend
   - ✅ Configure PM2 to run services
   - ✅ Configure Caddy reverse proxy with SSL
   - ✅ Start all services

4. **Configure API keys:**
   ```bash
   cd nasa_zeus
   nano .env
   ```

   Update these values:
   ```bash
   OPENWEATHER_API_KEY=your_actual_key_here
   OPENAQ_API_KEY=your_actual_key_here
   GEMINI_API_KEY=your_actual_key_here
   SECRET_KEY=$(openssl rand -hex 32)
   ```

5. **Restart services after updating .env:**
   ```bash
   pm2 restart all
   ```

6. **Verify deployment:**
   ```bash
   pm2 list
   pm2 logs
   sudo systemctl status caddy
   ```

### Phase 3: Verification

1. **Test locally on server:**
   ```bash
   curl http://localhost:8000/docs          # Backend API docs
   curl http://localhost:3000               # Frontend
   ```

2. **Test via domain:**
   ```bash
   curl https://nasazeus.org
   ```

3. **Visit in browser:**
   - https://nasazeus.org
   - https://nasazeus.org/api/docs (FastAPI docs)

## 🔧 Management Commands

### PM2 Process Management
```bash
# View all processes
pm2 list

# View logs
pm2 logs                # All logs
pm2 logs backend        # Backend logs only
pm2 logs frontend       # Frontend logs only

# Restart services
pm2 restart all         # Restart all
pm2 restart backend     # Restart backend only
pm2 restart frontend    # Restart frontend only

# Stop services
pm2 stop all
pm2 stop backend
pm2 stop frontend

# Delete processes
pm2 delete all
pm2 delete backend

# View detailed info
pm2 info backend
pm2 monit               # Real-time monitoring
```

### Caddy Management
```bash
# Check status
sudo systemctl status caddy

# Reload configuration
sudo systemctl reload caddy

# Restart Caddy
sudo systemctl restart caddy

# View logs
sudo tail -f /var/log/caddy/nasazeus.log

# Validate Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile

# View SSL certificate info
sudo caddy list-modules
```

### System Monitoring
```bash
# Check disk space
df -h

# Check memory usage
free -h

# View system resources
htop

# Check network connections
sudo netstat -tlnp
```

## 🔄 Updating the Application

### Update Backend Code
```bash
cd ~/nasa_zeus
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
deactivate
pm2 restart backend
```

### Update Frontend Code
```bash
cd ~/nasa_zeus/frontend
git pull origin main
npm install
npm run build
pm2 restart frontend
```

### Update Both
```bash
cd ~/nasa_zeus
git pull origin main

# Backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
pm2 restart backend

# Frontend
cd frontend
npm install
npm run build
pm2 restart frontend
```

## 🐛 Troubleshooting

### Backend Not Starting
```bash
# Check logs
pm2 logs backend

# Check if port 8000 is in use
sudo lsof -i :8000

# Test backend directly
cd ~/nasa_zeus
source venv/bin/activate
python3 main.py
```

### Frontend Not Starting
```bash
# Check logs
pm2 logs frontend

# Check if port 3000 is in use
sudo lsof -i :3000

# Test frontend directly
cd ~/nasa_zeus/frontend
npm run start
```

### Caddy SSL Issues
```bash
# Check Caddy logs
sudo journalctl -u caddy -n 50

# Verify DNS is pointing correctly
dig nasazeus.org

# Test Caddy configuration
sudo caddy validate --config /etc/caddy/Caddyfile

# Restart Caddy
sudo systemctl restart caddy
```

### Database Issues
```bash
# Recreate database
cd ~/nasa_zeus
source venv/bin/activate
python3 -c "from models.database import create_tables; create_tables()"
```

### Port Conflicts
```bash
# Find what's using a port
sudo lsof -i :8000
sudo lsof -i :3000

# Kill a process by PID
kill -9 [PID]
```

## 💰 Cost Management

### EC2 t3.small Pricing (us-east-1)
- **Hourly**: ~$0.0208
- **Daily**: ~$0.50
- **Monthly**: ~$15.00 (if running 24/7)

### Cost Optimization Tips

1. **Stop instance when not in use:**
   ```bash
   # From local machine
   aws ec2 stop-instances --instance-ids [INSTANCE_ID]
   
   # Start again
   aws ec2 start-instances --instance-ids [INSTANCE_ID]
   ```

2. **Monitor costs:**
   - Use AWS Cost Explorer
   - Set up billing alerts
   - Review CloudWatch metrics

3. **Consider Reserved Instances:**
   - If running 24/7 for 1+ year
   - Can save up to 72% vs On-Demand

## 🔒 Security Checklist

- ✅ SSH keys properly secured (chmod 400)
- ✅ Security group limits access (only ports 22, 80, 443)
- ✅ API keys stored in .env (not in code)
- ✅ Automatic HTTPS via Caddy/Let's Encrypt
- ✅ Security headers configured in Caddy
- ✅ Database uses proper authentication
- ✅ Regular system updates scheduled

### Additional Security Measures

1. **Setup firewall:**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

2. **Auto-security updates:**
   ```bash
   sudo apt-get install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

3. **Fail2ban (SSH protection):**
   ```bash
   sudo apt-get install fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

## 📊 Monitoring & Logging

### Setup CloudWatch Agent (Optional)
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Configure and start
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### Log Locations
- **PM2 Logs**: `~/.pm2/logs/`
- **Caddy Logs**: `/var/log/caddy/nasazeus.log`
- **System Logs**: `/var/log/syslog`
- **Application Logs**: Check PM2 logs

## 🔗 Useful Resources

- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [PM2 Documentation](https://pm2.keymetrics.io/docs/)
- [Caddy Documentation](https://caddyserver.com/docs/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

## 📞 Support

For issues specific to NASA ZEUS:
- GitHub Issues: https://github.com/codemith/nasa_zeus/issues
- Project Documentation: See main README.md

---

**Last Updated**: October 2025  
**Deployment Script Version**: 1.0  
**Tested On**: Ubuntu 22.04 LTS, AWS EC2 t3.small
