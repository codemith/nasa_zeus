#!/bin/bash
# NASA ZEUS Quick Redeploy Script
# Usage: ./deployment/quick-redeploy.sh

set -e  # Exit on error

echo "🚀 NASA ZEUS Quick Redeploy Script"
echo "=================================="
echo ""

# Configuration
KEY_PATH="deployment/nasa-zeus-key.pem"
SERVER="ubuntu@98.80.14.227"

echo "📡 Connecting to server..."

ssh -i "$KEY_PATH" "$SERVER" << 'ENDSSH'
set -e

echo "📦 Pulling latest code..."
cd nasa_zeus
git pull origin main

echo "🐍 Updating Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt -q

echo "⚙️  Configuring frontend environment..."
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=https://www.nasazeus.org
NEXT_PUBLIC_GEMINI_URL=https://www.nasazeus.org/gemini
NEXT_PUBLIC_SITE_URL=https://www.nasazeus.org
EOF

echo "🏗️  Building frontend..."
cd frontend
npm install --silent
npm run build

echo "♻️  Restarting services..."
cd ..
pm2 restart all

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
pm2 list

echo ""
echo "📋 Recent Logs:"
pm2 logs --lines 20 --nostream

echo ""
echo "🌐 Site: https://www.nasazeus.org"
ENDSSH

echo ""
echo "✅ Deployment successful!"
echo "🔍 Check the site: https://www.nasazeus.org"
