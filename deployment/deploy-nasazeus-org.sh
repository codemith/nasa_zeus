#!/bin/bash

################################################################################
# NASA ZEUS Comprehensive Deployment Script
# Deploy NASA ZEUS to AWS EC2 t3.small without Docker
# Domain: nasazeus.org
################################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
PROJECT_NAME="nasa_zeus"
GITHUB_REPO="https://github.com/codemith/nasa_zeus.git"
DOMAIN="nasazeus.org"
KEY_PAIR_NAME="nasa-zeus-key"
SECURITY_GROUP_NAME="nasazeus-sg"
INSTANCE_TAG="NASA-ZEUS-Server"
INSTANCE_TYPE="t3.small"

# Ubuntu 22.04 LTS AMI (update for your region)
# us-east-1: ami-0c7217cdde317cfec
# us-west-2: ami-0c55b159cbfafe1f0
AMI_ID="ami-0c7217cdde317cfec"

################################################################################
# PART 1: AWS INFRASTRUCTURE SETUP (Run on local machine)
################################################################################

setup_aws_infrastructure() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  PART 1: AWS Infrastructure Setup                     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
        echo "Install: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"
        exit 1
    fi
    
    # Check if AWS is configured
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS CLI is not configured. Run 'aws configure' first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ AWS CLI is installed and configured${NC}"
    
    # Create security group
    echo -e "${YELLOW}📡 Creating security group...${NC}"
    if aws ec2 describe-security-groups --group-names $SECURITY_GROUP_NAME &> /dev/null; then
        echo -e "${YELLOW}⚠️  Security group '$SECURITY_GROUP_NAME' already exists, skipping...${NC}"
        SG_ID=$(aws ec2 describe-security-groups --group-names $SECURITY_GROUP_NAME --query 'SecurityGroups[0].GroupId' --output text)
    else
        SG_ID=$(aws ec2 create-security-group \
            --group-name $SECURITY_GROUP_NAME \
            --description "Security group for NASA ZEUS web server" \
            --output text)
        echo -e "${GREEN}✅ Created security group: $SG_ID${NC}"
        
        # Allow SSH (Port 22)
        aws ec2 authorize-security-group-ingress \
            --group-name $SECURITY_GROUP_NAME \
            --protocol tcp --port 22 --cidr 0.0.0.0/0
        echo -e "${GREEN}✅ Allowed SSH (Port 22)${NC}"
        
        # Allow HTTP (Port 80)
        aws ec2 authorize-security-group-ingress \
            --group-name $SECURITY_GROUP_NAME \
            --protocol tcp --port 80 --cidr 0.0.0.0/0
        echo -e "${GREEN}✅ Allowed HTTP (Port 80)${NC}"
        
        # Allow HTTPS (Port 443)
        aws ec2 authorize-security-group-ingress \
            --group-name $SECURITY_GROUP_NAME \
            --protocol tcp --port 443 --cidr 0.0.0.0/0
        echo -e "${GREEN}✅ Allowed HTTPS (Port 443)${NC}"
    fi
    
    # Launch EC2 instance
    echo -e "${YELLOW}🚀 Launching EC2 t3.small instance...${NC}"
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_PAIR_NAME \
        --security-groups $SECURITY_GROUP_NAME \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_TAG}]" \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    echo -e "${GREEN}✅ Instance launched: $INSTANCE_ID${NC}"
    echo -e "${YELLOW}⏳ Waiting for instance to be running...${NC}"
    
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    
    # Get public IP
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)
    
    echo -e "${GREEN}✅ Instance is running!${NC}"
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Instance Details:                                     ║${NC}"
    echo -e "${BLUE}║  Instance ID: $INSTANCE_ID                          ║${NC}"
    echo -e "${BLUE}║  Public IP:   $PUBLIC_IP                             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    
    # Save details for later use
    echo "$INSTANCE_ID" > .deployment_instance_id
    echo "$PUBLIC_IP" > .deployment_public_ip
    
    echo ""
    echo -e "${YELLOW}📋 NEXT STEPS:${NC}"
    echo "1. Configure DNS A record for '$DOMAIN' to point to: $PUBLIC_IP"
    echo "2. Wait for DNS propagation (may take 5-60 minutes)"
    echo "3. SSH into the server: ssh -i '$KEY_PAIR_NAME.pem' ubuntu@$PUBLIC_IP"
    echo "4. Run the server setup section of this script on the EC2 instance"
    echo ""
    echo "To continue setup on server, copy this script and run:"
    echo "  scp -i '$KEY_PAIR_NAME.pem' deploy-nasazeus-org.sh ubuntu@$PUBLIC_IP:~/"
    echo "  ssh -i '$KEY_PAIR_NAME.pem' ubuntu@$PUBLIC_IP"
    echo "  bash deploy-nasazeus-org.sh server-setup"
}

################################################################################
# PART 2: SERVER SETUP & DEPLOYMENT (Run on EC2 instance)
################################################################################

server_setup() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  PART 2: Server Environment Setup                     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    
    # Update system
    echo -e "${YELLOW}📦 Updating system packages...${NC}"
    sudo apt-get update -y
    sudo apt-get upgrade -y
    
    # Install essential packages
    echo -e "${YELLOW}📦 Installing essential packages...${NC}"
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        nodejs \
        npm \
        git \
        curl \
        build-essential \
        libssl-dev
    
    # Install Node.js 18+ (if not already latest)
    echo -e "${YELLOW}📦 Installing Node.js 18...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    echo -e "${GREEN}✅ Node.js version: $(node --version)${NC}"
    echo -e "${GREEN}✅ npm version: $(npm --version)${NC}"
    
    # Install PM2 globally
    echo -e "${YELLOW}📦 Installing PM2 process manager...${NC}"
    sudo npm install -g pm2
    
    # Install Caddy web server
    echo -e "${YELLOW}📦 Installing Caddy web server...${NC}"
    sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
    sudo apt-get update
    sudo apt-get install -y caddy
    
    echo -e "${GREEN}✅ Caddy installed: $(caddy version)${NC}"
    
    # Clone project
    echo -e "${YELLOW}📥 Cloning NASA ZEUS project...${NC}"
    cd ~
    if [ -d "$PROJECT_NAME" ]; then
        echo -e "${YELLOW}⚠️  Project directory exists, pulling latest changes...${NC}"
        cd $PROJECT_NAME
        git pull
    else
        git clone $GITHUB_REPO
        cd $PROJECT_NAME
    fi
    
    PROJECT_DIR=$(pwd)
    echo -e "${GREEN}✅ Project directory: $PROJECT_DIR${NC}"
    
    # Setup backend
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Setting up FastAPI Backend                           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    
    cd $PROJECT_DIR
    
    # Create Python virtual environment
    echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install backend dependencies
    echo -e "${YELLOW}📚 Installing backend dependencies...${NC}"
    pip install -r requirements.txt
    
    # Install XGBoost (CPU version for ML model)
    echo -e "${YELLOW}🤖 Installing XGBoost for O3 predictions...${NC}"
    pip install "xgboost<2.0.0"
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        echo -e "${YELLOW}📝 Creating .env file...${NC}"
        cat > .env << 'EOF'
# Backend Environment Variables
DATABASE_URL=sqlite:///./nasa_zeus.db
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (UPDATE THESE!)
OPENWEATHER_API_KEY=your_openweather_key_here
OPENAQ_API_KEY=your_openaq_key_here
GEMINI_API_KEY=your_gemini_key_here

# NOAA API
NOAA_API_BASE=https://api.weather.gov

# Frontend URL
FRONTEND_URL=https://nasazeus.org
EOF
        echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env file and add your API keys!${NC}"
        echo -e "${YELLOW}   Run: nano .env${NC}"
    fi
    
    # Initialize database
    echo -e "${YELLOW}💾 Initializing database...${NC}"
    python3 -c "from models.database import create_tables; create_tables()"
    
    # Start backend with PM2
    echo -e "${YELLOW}🚀 Starting FastAPI backend with PM2...${NC}"
    pm2 delete backend 2>/dev/null || true
    pm2 start "$PROJECT_DIR/venv/bin/uvicorn" \
        --name "backend" \
        --cwd "$PROJECT_DIR" \
        -- main:app --host 0.0.0.0 --port 8000
    
    deactivate
    
    # Setup frontend
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Setting up Next.js Frontend                           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    
    cd $PROJECT_DIR/frontend
    
    # Install frontend dependencies
    echo -e "${YELLOW}📦 Installing frontend dependencies (this may take a while)...${NC}"
    npm install
    
    # Create .env.local for frontend
    if [ ! -f .env.local ]; then
        echo -e "${YELLOW}📝 Creating frontend .env.local...${NC}"
        cat > .env.local << EOF
NEXT_PUBLIC_API_URL=https://$DOMAIN/api
NEXT_PUBLIC_SITE_URL=https://$DOMAIN
EOF
    fi
    
    # Build frontend
    echo -e "${YELLOW}🏗️  Building Next.js production build...${NC}"
    npm run build
    
    # Start frontend with PM2
    echo -e "${YELLOW}🚀 Starting Next.js frontend with PM2...${NC}"
    pm2 delete frontend 2>/dev/null || true
    pm2 start npm \
        --name "frontend" \
        --cwd "$PROJECT_DIR/frontend" \
        -- start -- -p 3000
    
    # Setup Gemini AI server (optional)
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Setting up Gemini AI Server (Optional)               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    
    cd $PROJECT_DIR
    if [ -f "gemini_server.py" ]; then
        echo -e "${YELLOW}🤖 Starting Gemini AI server...${NC}"
        pm2 delete gemini-server 2>/dev/null || true
        pm2 start "$PROJECT_DIR/venv/bin/python3" \
            --name "gemini-server" \
            --cwd "$PROJECT_DIR" \
            -- gemini_server.py
    fi
    
    # Save PM2 configuration
    echo -e "${YELLOW}💾 Saving PM2 configuration...${NC}"
    pm2 save
    
    # Setup PM2 to start on system boot
    echo -e "${YELLOW}🔄 Configuring PM2 to start on boot...${NC}"
    sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u ubuntu --hp /home/ubuntu
    
    # Show PM2 status
    echo -e "${GREEN}✅ PM2 processes:${NC}"
    pm2 list
}

################################################################################
# PART 3: CONFIGURE REVERSE PROXY & SSL
################################################################################

configure_caddy() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  PART 3: Configuring Caddy Reverse Proxy & SSL        ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    
    echo -e "${YELLOW}📝 Creating Caddyfile configuration...${NC}"
    
    sudo bash -c "cat > /etc/caddy/Caddyfile" << 'EOF'
# NASA ZEUS Caddy Configuration
# Automatic HTTPS with Let's Encrypt

nasazeus.org, www.nasazeus.org {
    # Enable automatic HTTPS
    encode gzip
    
    # API routes to FastAPI backend
    handle /api/* {
        reverse_proxy localhost:8000
    }
    
    # Gemini AI routes (optional)
    handle /gemini/* {
        reverse_proxy localhost:8080
    }
    
    # WebSocket support for real-time updates
    @websockets {
        header Connection *Upgrade*
        header Upgrade websocket
    }
    reverse_proxy @websockets localhost:3000
    
    # All other routes to Next.js frontend
    reverse_proxy localhost:3000
    
    # Security headers
    header {
        # Enable HSTS
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        # Prevent clickjacking
        X-Frame-Options "SAMEORIGIN"
        # Prevent MIME type sniffing
        X-Content-Type-Options "nosniff"
        # XSS protection
        X-XSS-Protection "1; mode=block"
        # Referrer policy
        Referrer-Policy "strict-origin-when-cross-origin"
    }
    
    # Custom error pages
    handle_errors {
        @502-504 expression `{err.status_code} in [502, 503, 504]`
        handle @502-504 {
            respond "Service temporarily unavailable. Please try again shortly." 503
        }
    }
    
    # Logging
    log {
        output file /var/log/caddy/nasazeus.log
        format json
    }
}
EOF
    
    # Create log directory
    sudo mkdir -p /var/log/caddy
    sudo chown caddy:caddy /var/log/caddy
    
    # Validate Caddyfile
    echo -e "${YELLOW}✔️  Validating Caddyfile...${NC}"
    if sudo caddy validate --config /etc/caddy/Caddyfile; then
        echo -e "${GREEN}✅ Caddyfile is valid${NC}"
    else
        echo -e "${RED}❌ Caddyfile has errors!${NC}"
        exit 1
    fi
    
    # Reload Caddy
    echo -e "${YELLOW}🔄 Reloading Caddy...${NC}"
    sudo systemctl reload caddy
    
    # Enable Caddy to start on boot
    sudo systemctl enable caddy
    
    echo -e "${GREEN}✅ Caddy configured and running${NC}"
}

################################################################################
# PART 4: FINAL CHECKS & MONITORING
################################################################################

final_checks() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  PART 4: Final Checks & Monitoring Setup              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    
    echo -e "${YELLOW}🔍 Checking service status...${NC}"
    
    # Check PM2 processes
    echo -e "\n${BLUE}PM2 Processes:${NC}"
    pm2 list
    
    # Check Caddy status
    echo -e "\n${BLUE}Caddy Status:${NC}"
    sudo systemctl status caddy --no-pager | head -n 15
    
    # Test backend endpoint
    echo -e "\n${YELLOW}🧪 Testing backend API...${NC}"
    if curl -s http://localhost:8000/docs > /dev/null; then
        echo -e "${GREEN}✅ Backend API is responding${NC}"
    else
        echo -e "${RED}❌ Backend API is not responding${NC}"
    fi
    
    # Test frontend
    echo -e "\n${YELLOW}🧪 Testing frontend...${NC}"
    if curl -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✅ Frontend is responding${NC}"
    else
        echo -e "${RED}❌ Frontend is not responding${NC}"
    fi
    
    # Display useful commands
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Useful Commands:                                      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo -e "${YELLOW}PM2 Commands:${NC}"
    echo "  pm2 list              - List all processes"
    echo "  pm2 logs              - View all logs"
    echo "  pm2 logs backend      - View backend logs"
    echo "  pm2 logs frontend     - View frontend logs"
    echo "  pm2 restart all       - Restart all processes"
    echo "  pm2 stop all          - Stop all processes"
    echo ""
    echo -e "${YELLOW}Caddy Commands:${NC}"
    echo "  sudo systemctl status caddy   - Check Caddy status"
    echo "  sudo systemctl reload caddy   - Reload Caddy config"
    echo "  sudo caddy validate --config /etc/caddy/Caddyfile  - Validate config"
    echo "  sudo tail -f /var/log/caddy/nasazeus.log           - View access logs"
    echo ""
    echo -e "${YELLOW}System Commands:${NC}"
    echo "  sudo systemctl status         - View all services"
    echo "  df -h                         - Check disk space"
    echo "  free -h                       - Check memory usage"
    echo "  htop                          - System monitor"
}

################################################################################
# DEPLOYMENT COMPLETION
################################################################################

deployment_complete() {
    echo -e "\n${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                        ║${NC}"
    echo -e "${GREEN}║  🎉 NASA ZEUS DEPLOYMENT COMPLETE! 🎉                  ║${NC}"
    echo -e "${GREEN}║                                                        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    
    echo -e "\n${BLUE}Your site should be live at:${NC}"
    echo -e "${GREEN}🌐 https://$DOMAIN${NC}"
    echo -e "${GREEN}🌐 https://www.$DOMAIN${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT REMINDERS:${NC}"
    echo "1. ✅ Update API keys in .env file"
    echo "2. ✅ Verify DNS A record points to your server IP"
    echo "3. ✅ SSL certificate will be automatically obtained by Caddy"
    echo "4. ✅ Monitor logs with: pm2 logs"
    echo "5. ✅ Set up monitoring and backups"
    echo "6. 💰 Remember to stop/terminate EC2 instance when done testing"
    echo ""
    echo -e "${BLUE}Cost Management:${NC}"
    echo "  - t3.small costs ~\$0.0208/hour (~\$15/month if running 24/7)"
    echo "  - Stop instance when not in use to save costs"
    echo "  - Use AWS Cost Explorer to monitor spending"
    echo ""
    echo -e "${GREEN}🚀 Happy deploying!${NC}"
}

################################################################################
# MAIN SCRIPT EXECUTION
################################################################################

main() {
    case "${1:-}" in
        "aws-setup"|"setup-aws"|"infrastructure")
            setup_aws_infrastructure
            ;;
        "server-setup"|"setup-server"|"deploy")
            server_setup
            configure_caddy
            final_checks
            deployment_complete
            ;;
        "configure-caddy"|"caddy")
            configure_caddy
            ;;
        "check"|"status")
            final_checks
            ;;
        "full"|"complete"|"")
            echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
            echo -e "${RED}║  FULL DEPLOYMENT CANNOT BE RUN FROM ONE MACHINE       ║${NC}"
            echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
            echo ""
            echo "This script must be run in two phases:"
            echo ""
            echo -e "${YELLOW}Phase 1 (Local Machine):${NC}"
            echo "  bash deploy-nasazeus-org.sh aws-setup"
            echo ""
            echo -e "${YELLOW}Phase 2 (EC2 Instance):${NC}"
            echo "  bash deploy-nasazeus-org.sh server-setup"
            echo ""
            exit 1
            ;;
        *)
            echo -e "${RED}Unknown command: $1${NC}"
            echo ""
            echo "Usage: bash deploy-nasazeus-org.sh [command]"
            echo ""
            echo "Commands:"
            echo "  aws-setup      - Setup AWS infrastructure (run on local machine)"
            echo "  server-setup   - Setup server environment (run on EC2 instance)"
            echo "  configure-caddy - Configure Caddy reverse proxy"
            echo "  check          - Check deployment status"
            echo ""
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
