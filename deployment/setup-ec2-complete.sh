#!/bin/bash
# Complete EC2 Setup Script for NASA Zeus Application
# Run this script on your EC2 instance after initial connection

set -e  # Exit on any error

echo "🚀 NASA Zeus - Complete EC2 Setup Script"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo dnf update -y

# Install Python 3 and pip
echo "🐍 Installing Python 3 and pip..."
sudo dnf install -y python3 python3-pip python3-devel gcc

# Install Node.js (version 18+)
echo "📦 Installing Node.js 18..."
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install -y nodejs

# Verify installations
echo "✅ Verifying installations..."
python3 --version
pip3 --version
node --version
npm --version

# Create application directory if it doesn't exist
cd ~

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip3 install --user --no-cache-dir fastapi uvicorn[standard] httpx python-jose[cryptography] \
    passlib[bcrypt] python-multipart SQLAlchemy google-generativeai python-dotenv \
    pandas numpy scikit-learn email-validator pydantic

# Install XGBoost (CPU version, no CUDA)
echo "🤖 Installing XGBoost (CPU-only version)..."
pip3 install --user --no-cache-dir "xgboost<2.0.0"

# Create .env file for backend if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# Backend Environment Variables
DATABASE_URL=sqlite:///./nasa_zeus.db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Gemini API Key
GEMINI_API_KEY=your-gemini-api-key-here

# NASA API (optional)
NASA_API_KEY=DEMO_KEY
EOF
    echo "⚠️  Please update .env with your actual API keys!"
fi

# Setup frontend
if [ -d "frontend" ]; then
    cd frontend
    
    # Create frontend .env
    INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    echo "📝 Creating frontend .env with IP: $INSTANCE_IP"
    
    cat > .env << EOF
NEXT_PUBLIC_API_URL=http://${INSTANCE_IP}:8000
NEXT_PUBLIC_GEMINI_URL=http://${INSTANCE_IP}:8001
EOF
    
    # Install npm packages
    echo "📦 Installing npm packages..."
    npm install --legacy-peer-deps
    
    # Build frontend
    echo "🏗️  Building frontend..."
    npm run build
    
    cd ~
fi

# Create startup script
echo "📝 Creating startup script..."
cat > ~/start-all-services.sh << 'EOF'
#!/bin/bash
# Start all NASA Zeus services

echo "🚀 Starting NASA Zeus services..."

# Kill any existing processes
pkill -f "uvicorn main:app" || true
pkill -f "gemini_server.py" || true
pkill -f "npm.*start" || true

# Start backend API
echo "Starting backend API on port 8000..."
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

# Wait a bit for backend to start
sleep 3

# Start Gemini AI service
echo "Starting Gemini AI service on port 8001..."
nohup python3 gemini_server.py > gemini.log 2>&1 &

# Wait a bit
sleep 3

# Start frontend
echo "Starting frontend on port 3000..."
cd frontend
nohup npm start > ../frontend.log 2>&1 &
cd ~

sleep 5

# Check status
echo ""
echo "✅ Service Status:"
echo "=================="
ps aux | grep -E "uvicorn|gemini_server|npm.*start" | grep -v grep

echo ""
echo "🌐 Application URLs:"
echo "Frontend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"
echo "Backend API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "Gemini API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8001"
echo ""
echo "📋 View logs:"
echo "  Backend: tail -f ~/backend.log"
echo "  Gemini: tail -f ~/gemini.log"
echo "  Frontend: tail -f ~/frontend.log"
EOF

chmod +x ~/start-all-services.sh

# Create stop script
echo "📝 Creating stop script..."
cat > ~/stop-all-services.sh << 'EOF'
#!/bin/bash
# Stop all NASA Zeus services

echo "🛑 Stopping NASA Zeus services..."

pkill -f "uvicorn main:app"
pkill -f "gemini_server.py"
pkill -f "npm.*start"

echo "✅ All services stopped"
EOF

chmod +x ~/stop-all-services.sh

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Update .env with your actual API keys (especially GEMINI_API_KEY)"
echo "2. Start all services: ./start-all-services.sh"
echo "3. Access your app at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"
echo ""
echo "Useful commands:"
echo "  Start services: ./start-all-services.sh"
echo "  Stop services: ./stop-all-services.sh"
echo "  View backend logs: tail -f backend.log"
echo "  View Gemini logs: tail -f gemini.log"
echo "  View frontend logs: tail -f frontend.log"
echo ""
