#!/bin/bash

# =============================================================================
# NASA Zeus - Secure Environment Setup Script
# =============================================================================

set -e  # Exit on error

echo "🔐 NASA Zeus - Security Setup"
echo "=============================="
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted. Using existing .env file."
        exit 0
    fi
fi

# Copy .env.example to .env
echo "📋 Creating .env from template..."
cp .env.example .env

# Generate JWT secret
echo ""
echo "🔑 Generating JWT secret key..."
if command -v openssl &> /dev/null; then
    JWT_SECRET=$(openssl rand -hex 32)
elif command -v python3 &> /dev/null; then
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
else
    echo "❌ Error: Neither openssl nor python3 found. Cannot generate JWT secret."
    echo "Please install one of them or manually add JWT_SECRET_KEY to .env"
    exit 1
fi

# Update JWT secret in .env
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env
else
    # Linux
    sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env
fi

echo "✅ JWT secret generated and saved"

# Prompt for API keys
echo ""
echo "📝 Now let's set up your API keys"
echo "=================================="
echo ""

# OpenWeatherMap
read -p "Enter your OpenWeatherMap API key (or press Enter to skip): " OPENWEATHER_KEY
if [ ! -z "$OPENWEATHER_KEY" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/OPENWEATHER_API_KEY=.*/OPENWEATHER_API_KEY=$OPENWEATHER_KEY/" .env
    else
        sed -i "s/OPENWEATHER_API_KEY=.*/OPENWEATHER_API_KEY=$OPENWEATHER_KEY/" .env
    fi
    echo "✅ OpenWeatherMap API key saved"
fi

# Gemini
read -p "Enter your Gemini API key (or press Enter to skip): " GEMINI_KEY
if [ ! -z "$GEMINI_KEY" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$GEMINI_KEY/" .env
    else
        sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$GEMINI_KEY/" .env
    fi
    echo "✅ Gemini API key saved"
fi

# OpenAQ (optional)
read -p "Enter your OpenAQ API key (optional, press Enter to skip): " OPENAQ_KEY
if [ ! -z "$OPENAQ_KEY" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/OPENAQ_API_KEY=.*/OPENAQ_API_KEY=$OPENAQ_KEY/" .env
    else
        sed -i "s/OPENAQ_API_KEY=.*/OPENAQ_API_KEY=$OPENAQ_KEY/" .env
    fi
    echo "✅ OpenAQ API key saved"
fi

# Setup frontend environment
echo ""
echo "🎨 Setting up frontend environment..."
cd frontend

if [ -f ".env.local" ]; then
    echo "⚠️  frontend/.env.local already exists, skipping..."
else
    cp .env.example .env.local
    echo "✅ frontend/.env.local created"
fi

cd ..

# Verify .gitignore
echo ""
echo "🔍 Verifying .gitignore..."
if grep -q "^\.env$" .gitignore; then
    echo "✅ .env is in .gitignore"
else
    echo ".env" >> .gitignore
    echo "✅ Added .env to .gitignore"
fi

if grep -q "frontend/\.env\.local" .gitignore; then
    echo "✅ frontend/.env.local is in .gitignore"
else
    echo "frontend/.env.local" >> .gitignore
    echo "✅ Added frontend/.env.local to .gitignore"
fi

# Check if .env is tracked by git
if git ls-files --error-unmatch .env &> /dev/null; then
    echo ""
    echo "⚠️  WARNING: .env is currently tracked by git!"
    echo "   Run: git rm --cached .env"
    echo "   Then commit the change"
fi

# Summary
echo ""
echo "=============================="
echo "✅ Security setup complete!"
echo "=============================="
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Review and update .env with any missing API keys"
echo "2. Get API keys from:"
echo "   - OpenWeatherMap: https://openweathermap.org/api"
echo "   - Gemini AI: https://aistudio.google.com/app/apikey"
echo "   - OpenAQ: https://openaq.org/"
echo ""
echo "3. Update frontend/.env.local for production deployment"
echo ""
echo "4. NEVER commit .env files to git!"
echo ""
echo "5. Start your app:"
echo "   Backend:  uvicorn main:app --reload"
echo "   Frontend: cd frontend && npm run dev"
echo ""
echo "📖 Read SECURITY_DEPLOYMENT_GUIDE.md for deployment instructions"
echo ""
