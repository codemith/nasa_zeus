#!/bin/bash

# =============================================================================
# NASA Zeus AWS Deployment Script
# =============================================================================
# This script automates the deployment of NASA Zeus to AWS EC2
# 
# Prerequisites:
# - AWS CLI configured with credentials
# - Docker installed on local machine
# - .env file configured with API keys
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGION="us-east-1"
AMI_ID="ami-0c02fb55d7b3d91df"  # Amazon Linux 2023 (check for latest)
INSTANCE_TYPE="t3.small"  # t3.small for Docker deployment (2 vCPU, 2GB RAM) - good balance
KEY_NAME="nasa-zeus-key"
SECURITY_GROUP_NAME="nasa-zeus-sg"
INSTANCE_NAME="nasa-zeus-app"

echo -e "${BLUE}🚀 NASA Zeus AWS Deployment Script${NC}"
echo "=================================="
echo ""

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi
print_success "AWS CLI installed"

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install it first."
    exit 1
fi
print_success "Docker installed"

# Check for .env file in parent directory (root of project)
if [ ! -f "../.env" ]; then
    print_error ".env file not found in parent directory. Please create it in the root directory."
    exit 1
fi
print_success ".env file found"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi
print_success "AWS credentials configured"

echo ""
echo -e "${YELLOW}⚙️  Configuration:${NC}"
echo "Region: $REGION"
echo "Instance Type: $INSTANCE_TYPE"
echo "Key Name: $KEY_NAME"
echo ""

read -p "Do you want to proceed with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Deployment cancelled"
    exit 0
fi

# Step 1: Create Security Group
echo ""
echo -e "${BLUE}🔒 Step 1: Creating security group...${NC}"

SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --region $REGION 2>/dev/null)

if [ "$SECURITY_GROUP_ID" == "None" ] || [ -z "$SECURITY_GROUP_ID" ]; then
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Security group for NASA Zeus application" \
        --region $REGION \
        --query 'GroupId' \
        --output text)
    
    print_success "Security group created: $SECURITY_GROUP_ID"
    
    # Add inbound rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 22 --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null || true
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 80 --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null || true
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp --port 443 --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null || true
    
    print_success "Security group rules configured"
else
    print_info "Security group already exists: $SECURITY_GROUP_ID"
fi

# Step 2: Create Key Pair
echo ""
echo -e "${BLUE}🔑 Step 2: Creating key pair...${NC}"

if [ ! -f "$KEY_NAME.pem" ]; then
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text \
        --region $REGION > $KEY_NAME.pem
    
    chmod 400 $KEY_NAME.pem
    print_success "Key pair created: $KEY_NAME.pem"
    print_warning "IMPORTANT: Save this key file! You won't be able to download it again."
else
    print_info "Key pair already exists: $KEY_NAME.pem"
fi

# Step 3: Get latest Amazon Linux 2023 AMI
echo ""
echo -e "${BLUE}🖼️  Step 3: Finding latest Amazon Linux AMI...${NC}"

AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=al2023-ami-2023*-x86_64" \
              "Name=state,Values=available" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text \
    --region $REGION)

print_success "Using AMI: $AMI_ID"

# Step 4: Launch EC2 Instance
echo ""
echo -e "${BLUE}🖥️  Step 4: Launching EC2 instance...${NC}"

# Check if instance already exists
EXISTING_INSTANCE=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=$INSTANCE_NAME" \
              "Name=instance-state-name,Values=running,stopped" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text \
    --region $REGION 2>/dev/null)

if [ "$EXISTING_INSTANCE" != "None" ] && [ -n "$EXISTING_INSTANCE" ]; then
    print_warning "Instance already exists: $EXISTING_INSTANCE"
    INSTANCE_ID=$EXISTING_INSTANCE
    
    read -p "Do you want to use this existing instance? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Please terminate the existing instance first or use a different name."
        exit 0
    fi
else
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_NAME \
        --security-group-ids $SECURITY_GROUP_ID \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
        --region $REGION \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    print_success "EC2 instance launched: $INSTANCE_ID"
    
    print_info "Waiting for instance to be running..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION
    print_success "Instance is running"
fi

# Get instance public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text \
    --region $REGION)

print_success "Instance Public IP: $PUBLIC_IP"

# Step 5: Wait for SSH to be available
echo ""
echo -e "${BLUE}⏳ Step 5: Waiting for SSH to be available...${NC}"
print_info "This may take a few minutes..."

sleep 30  # Initial wait for instance to fully boot

MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if ssh -i $KEY_NAME.pem -o StrictHostKeyChecking=no -o ConnectTimeout=5 ec2-user@$PUBLIC_IP "echo 'SSH Ready'" &> /dev/null; then
        print_success "SSH connection established"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo -n "."
    sleep 10
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "Failed to establish SSH connection after $MAX_RETRIES attempts"
    exit 1
fi

# Step 6: Setup instance
echo ""
echo -e "${BLUE}⚙️  Step 6: Setting up instance...${NC}"

print_info "Installing Docker and dependencies..."
ssh -i $KEY_NAME.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << 'ENDSSH'
    set -e
    
    # Update system
    sudo yum update -y
    
    # Install Docker
    sudo yum install -y docker git
    sudo service docker start
    sudo usermod -a -G docker ec2-user
    
    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo "✅ Docker and dependencies installed"
ENDSSH

print_success "Instance setup complete"

# Step 7: Deploy application
echo ""
echo -e "${BLUE}📦 Step 7: Deploying application...${NC}"

print_info "Copying files to instance..."

# Create tarball of repository (excluding unnecessary files)
print_info "Creating tarball of repository..."
cd ..
tar --exclude='node_modules' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.next' \
    --exclude='deployment/nasa-zeus-key.pem' \
    -czf deployment/nasa-zeus.tar.gz .
cd deployment

# Copy files to instance
print_info "Uploading files to instance..."
scp -i $KEY_NAME.pem -o StrictHostKeyChecking=no ../.env ec2-user@$PUBLIC_IP:~/
scp -i $KEY_NAME.pem -o StrictHostKeyChecking=no nasa-zeus.tar.gz ec2-user@$PUBLIC_IP:~/

# Extract and setup on instance
ssh -i $KEY_NAME.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << 'ENDSSH'
    echo "Extracting repository..."
    mkdir -p nasa-zeus
    tar -xzf nasa-zeus.tar.gz -C nasa-zeus
    rm nasa-zeus.tar.gz
ENDSSH

# Clean up local tarball
rm -f nasa-zeus.tar.gz

# Copy .env to repository and deploy
ssh -i $KEY_NAME.pem -o StrictHostKeyChecking=no ec2-user@$PUBLIC_IP << 'ENDSSH'
    cp ~/.env ~/nasa-zeus/.env
    cd ~/nasa-zeus/deployment
    
    # Build and start containers (requires new shell for docker group)
    sudo docker-compose down 2>/dev/null || true
    sudo docker-compose build
    sudo docker-compose up -d
    
    echo "✅ Application deployed and running"
ENDSSH

print_success "Application deployed successfully!"

# Final output
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${BLUE}Instance Details:${NC}"
echo "  Instance ID: $INSTANCE_ID"
echo "  Public IP: $PUBLIC_IP"
echo "  Region: $REGION"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo "  Frontend: http://$PUBLIC_IP"
echo "  Backend API: http://$PUBLIC_IP/api/health"
echo "  Gemini AI: http://$PUBLIC_IP/gemini/docs"
echo "  SSH: ssh -i $KEY_NAME.pem ec2-user@$PUBLIC_IP"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Configure your domain DNS to point to: $PUBLIC_IP"
echo "  2. Setup SSL certificate (see AWS_DEPLOYMENT_GUIDE.md)"
echo "  3. Update CORS settings in main.py for production domain"
echo "  4. Setup RDS database (optional, for production)"
echo "  5. Configure CloudWatch monitoring"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  View logs: ssh -i $KEY_NAME.pem ec2-user@$PUBLIC_IP 'cd nasa-zeus && docker-compose logs -f'"
echo "  Restart: ssh -i $KEY_NAME.pem ec2-user@$PUBLIC_IP 'cd nasa-zeus && docker-compose restart'"
echo "  Update: ssh -i $KEY_NAME.pem ec2-user@$PUBLIC_IP 'cd nasa-zeus && git pull && docker-compose up -d --build'"
echo ""
print_success "Deployment script completed!"
