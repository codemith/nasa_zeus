# 🚀 Quick Start: Deploy NASA ZEUS to nasazeus.org

## ⚡ TL;DR

Two-phase deployment: AWS setup (local) → Server setup (EC2)

---

## 📋 Phase 1: AWS Setup (5 minutes)

**Run on your local machine:**

```bash
cd deployment
./deploy-nasazeus-org.sh aws-setup
```

**Then:**
1. Note the EC2 Public IP from output
2. Go to your domain registrar
3. Create A record: `nasazeus.org` → `[EC2_PUBLIC_IP]`
4. Create A record: `www.nasazeus.org` → `[EC2_PUBLIC_IP]`
5. Wait 10-15 minutes for DNS propagation

---

## 📋 Phase 2: Server Setup (10 minutes)

**Copy script to server:**
```bash
scp -i nasa-zeus-key.pem deploy-nasazeus-org.sh ubuntu@[EC2_PUBLIC_IP]:~/
```

**SSH into server:**
```bash
ssh -i nasa-zeus-key.pem ubuntu@[EC2_PUBLIC_IP]
```

**Run deployment:**
```bash
chmod +x deploy-nasazeus-org.sh
./deploy-nasazeus-org.sh server-setup
```

**Update API keys:**
```bash
cd nasa_zeus
nano .env
# Update OPENWEATHER_API_KEY, OPENAQ_API_KEY, GEMINI_API_KEY
pm2 restart all
```

**Done!** Visit https://nasazeus.org 🎉

---

## 🔍 Quick Checks

```bash
pm2 list                           # Check running processes
pm2 logs                           # View logs
sudo systemctl status caddy        # Check Caddy status
curl http://localhost:8000/docs    # Test backend
curl http://localhost:3000         # Test frontend
```

---

## 🆘 Quick Fixes

**Backend issues:**
```bash
pm2 restart backend
pm2 logs backend
```

**Frontend issues:**
```bash
pm2 restart frontend
pm2 logs frontend
```

**SSL not working:**
```bash
sudo systemctl restart caddy
sudo journalctl -u caddy -n 50
```

---

## 💰 Cost Management

**Stop instance (save money):**
```bash
aws ec2 stop-instances --instance-ids [INSTANCE_ID]
```

**Start instance:**
```bash
aws ec2 start-instances --instance-ids [INSTANCE_ID]
```

**Cost**: ~$15/month if running 24/7, ~$0.50/day

---

## 📚 Full Documentation

See `DEPLOY_NASAZEUS_ORG.md` for complete guide with troubleshooting.
