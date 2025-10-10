# 📋 NASA ZEUS Deployment Checklist

Use this checklist to ensure you have everything ready before deploying.

## ✅ Pre-Deployment Requirements

### AWS Account Setup
- [ ] AWS account created
- [ ] AWS CLI installed locally
- [ ] AWS CLI configured (`aws configure` completed)
- [ ] IAM user has EC2 full access permissions
- [ ] EC2 key pair created (nasa-zeus-key.pem)
- [ ] Key pair file downloaded and secured (chmod 400)
- [ ] Default VPC available in target region

### Domain Configuration
- [ ] Domain registered: nasazeus.org
- [ ] Access to domain registrar DNS settings
- [ ] Know how to create A records

### API Keys Acquired
- [ ] OpenWeatherMap API key obtained
- [ ] OpenAQ API key obtained (optional)
- [ ] Google Gemini API key obtained
- [ ] API keys documented securely

### Local Environment
- [ ] Git repository cloned
- [ ] AWS CLI version 2+ installed
- [ ] SSH client available
- [ ] Internet connection stable

---

## ✅ Phase 1: AWS Infrastructure

### Before Running Script
- [ ] Reviewed deployment script configuration
- [ ] Updated AMI_ID for your AWS region
- [ ] Updated KEY_PAIR_NAME to match your key
- [ ] Script is executable (chmod +x)

### After Running Script
- [ ] EC2 instance created successfully
- [ ] Security group configured (ports 22, 80, 443)
- [ ] Public IP address noted and saved
- [ ] Instance ID saved for later reference

### DNS Configuration
- [ ] A record created: nasazeus.org → [EC2_IP]
- [ ] A record created: www.nasazeus.org → [EC2_IP]
- [ ] DNS propagation verified (dig/nslookup)
- [ ] Can ping the domain

---

## ✅ Phase 2: Server Setup

### Before Deployment
- [ ] Script copied to EC2 instance
- [ ] SSH connection to EC2 working
- [ ] Script is executable on server

### During Deployment
- [ ] System packages updated
- [ ] Python 3 installed
- [ ] Node.js 18+ installed
- [ ] PM2 installed
- [ ] Caddy installed
- [ ] Repository cloned
- [ ] Backend dependencies installed
- [ ] Frontend built successfully
- [ ] PM2 processes started
- [ ] Caddy configured

### After Deployment
- [ ] Backend API responding (localhost:8000)
- [ ] Frontend responding (localhost:3000)
- [ ] PM2 showing all processes running
- [ ] Caddy service active
- [ ] SSL certificate obtained automatically
- [ ] No errors in PM2 logs
- [ ] No errors in Caddy logs

---

## ✅ Configuration

### Environment Variables
- [ ] .env file created in project root
- [ ] DATABASE_URL configured
- [ ] SECRET_KEY generated (openssl rand -hex 32)
- [ ] ALGORITHM set to HS256
- [ ] ACCESS_TOKEN_EXPIRE_MINUTES set
- [ ] OPENWEATHER_API_KEY added
- [ ] OPENAQ_API_KEY added (if available)
- [ ] GEMINI_API_KEY added
- [ ] NOAA_API_BASE set
- [ ] FRONTEND_URL set to https://nasazeus.org

### Frontend Environment
- [ ] .env.local created in frontend/
- [ ] NEXT_PUBLIC_API_URL set
- [ ] NEXT_PUBLIC_SITE_URL set

---

## ✅ Testing & Verification

### Local Testing (on EC2)
- [ ] Backend API docs accessible: http://localhost:8000/docs
- [ ] Frontend accessible: http://localhost:3000
- [ ] Can register a test user
- [ ] Can login with test user
- [ ] API endpoints responding correctly

### Domain Testing
- [ ] Site accessible: https://nasazeus.org
- [ ] SSL certificate valid (green lock)
- [ ] www redirect works
- [ ] API endpoints work through domain
- [ ] No mixed content warnings
- [ ] No console errors in browser

### Functionality Testing
- [ ] Map loads correctly
- [ ] Air quality data displays
- [ ] Weather forecasts work
- [ ] O3 predictions load
- [ ] User authentication works
- [ ] Gemini AI chat works (if enabled)
- [ ] All data sources responding

---

## ✅ Performance & Monitoring

### System Health
- [ ] CPU usage under 80%
- [ ] Memory usage under 80%
- [ ] Disk space > 20% free
- [ ] No process crashes in PM2
- [ ] Response times acceptable (<2s)

### Monitoring Setup
- [ ] PM2 configured to restart on failure
- [ ] PM2 startup script enabled
- [ ] Caddy logs rotating properly
- [ ] CloudWatch agent installed (optional)
- [ ] Log monitoring solution in place

---

## ✅ Security Hardening

### Access Control
- [ ] SSH key secured (chmod 400)
- [ ] Only necessary ports open (22, 80, 443)
- [ ] SSH root login disabled
- [ ] Password authentication disabled
- [ ] UFW firewall enabled and configured

### Application Security
- [ ] API keys not in code/git
- [ ] SECRET_KEY is strong and unique
- [ ] CORS configured correctly
- [ ] Security headers set in Caddy
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] Database credentials secured

### Ongoing Security
- [ ] Unattended-upgrades configured
- [ ] Fail2ban installed and configured
- [ ] Regular backup strategy planned
- [ ] AWS security groups reviewed
- [ ] CloudWatch alarms configured

---

## ✅ Documentation & Handoff

### Documentation
- [ ] Deployment notes documented
- [ ] API keys documented securely
- [ ] Architecture diagram available
- [ ] Troubleshooting guide accessible
- [ ] Update procedures documented

### Team Knowledge
- [ ] Team knows how to access server
- [ ] Team knows how to check logs
- [ ] Team knows how to restart services
- [ ] Team knows how to deploy updates
- [ ] Emergency contacts listed

---

## ✅ Cost Management

### AWS Optimization
- [ ] Instance type appropriate (t3.small)
- [ ] No unused resources running
- [ ] Billing alerts configured
- [ ] Cost Explorer enabled
- [ ] Budget set in AWS
- [ ] Auto-shutdown scheduled (if applicable)

### Monitoring Costs
- [ ] Daily cost estimate: ~$0.50
- [ ] Monthly cost estimate: ~$15
- [ ] Stop/terminate plan for testing
- [ ] Production cost approved

---

## ✅ Backup & Recovery

### Backup Strategy
- [ ] Database backup scheduled
- [ ] Configuration files backed up
- [ ] .env files backed up securely
- [ ] SSL certificates backed up
- [ ] Code repository up to date

### Recovery Plan
- [ ] Instance AMI created (snapshot)
- [ ] Recovery procedure documented
- [ ] RTO/RPO defined
- [ ] Disaster recovery tested

---

## ✅ Post-Deployment

### Immediate Tasks (within 24 hours)
- [ ] Monitor logs for errors
- [ ] Check performance metrics
- [ ] Verify all features working
- [ ] Test under load
- [ ] Collect initial user feedback

### First Week Tasks
- [ ] Review CloudWatch metrics
- [ ] Optimize performance bottlenecks
- [ ] Update documentation based on issues
- [ ] Plan feature updates
- [ ] Review security logs

### Ongoing Maintenance
- [ ] Weekly log reviews scheduled
- [ ] Monthly security updates scheduled
- [ ] Quarterly cost reviews scheduled
- [ ] Backup verification scheduled
- [ ] Performance monitoring active

---

## 🎉 Deployment Complete!

When all items are checked:
- ✅ Deployment is production-ready
- ✅ All critical systems operational
- ✅ Security measures in place
- ✅ Monitoring and alerts active
- ✅ Team is prepared

**Congratulations on your successful NASA ZEUS deployment!** 🚀

---

**Document Version**: 1.0  
**Last Updated**: October 2025  
**Next Review**: Before next major deployment
