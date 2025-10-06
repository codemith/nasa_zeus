#!/bin/bash

# =============================================================================
# NASA Zeus - Security Verification Script
# =============================================================================

echo "🔍 NASA Zeus - Security Verification"
echo "====================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0

# Check 1: .env exists
echo "1. Checking if .env file exists..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ PASS${NC}: .env file exists"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}: .env file not found"
    echo "   Run: ./setup_security.sh"
    ((FAIL++))
fi

# Check 2: .env is in .gitignore
echo ""
echo "2. Checking if .env is in .gitignore..."
if grep -q "^\.env$" .gitignore; then
    echo -e "${GREEN}✅ PASS${NC}: .env is in .gitignore"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}: .env is NOT in .gitignore"
    echo "   Add: echo '.env' >> .gitignore"
    ((FAIL++))
fi

# Check 3: .env is not tracked by git
echo ""
echo "3. Checking if .env is tracked by git..."
if git ls-files --error-unmatch .env &> /dev/null; then
    echo -e "${RED}❌ FAIL${NC}: .env is tracked by git!"
    echo "   Run: git rm --cached .env && git commit -m 'Remove .env from tracking'"
    ((FAIL++))
else
    echo -e "${GREEN}✅ PASS${NC}: .env is not tracked by git"
    ((PASS++))
fi

# Check 4: JWT secret is set
echo ""
echo "4. Checking JWT secret key..."
if [ -f ".env" ]; then
    JWT_SECRET=$(grep "^JWT_SECRET_KEY=" .env | cut -d '=' -f2)
    if [ ! -z "$JWT_SECRET" ] && [ "$JWT_SECRET" != "your-super-secret-jwt-key-change-this-in-production" ]; then
        echo -e "${GREEN}✅ PASS${NC}: JWT secret is configured (${JWT_SECRET:0:10}...)"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC}: JWT secret is not configured or using default"
        echo "   Run: ./setup_security.sh"
        ((FAIL++))
    fi
fi

# Check 5: OpenWeatherMap API key
echo ""
echo "5. Checking OpenWeatherMap API key..."
if [ -f ".env" ]; then
    OW_KEY=$(grep "^OPENWEATHER_API_KEY=" .env | cut -d '=' -f2)
    if [ ! -z "$OW_KEY" ] && [ "$OW_KEY" != "your-openweather-api-key-here" ]; then
        echo -e "${GREEN}✅ PASS${NC}: OpenWeatherMap API key is set (${OW_KEY:0:10}...)"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️  WARN${NC}: OpenWeatherMap API key not set"
        ((WARN++))
    fi
fi

# Check 6: Gemini API key
echo ""
echo "6. Checking Gemini API key..."
if [ -f ".env" ]; then
    GEMINI_KEY=$(grep "^GEMINI_API_KEY=" .env | cut -d '=' -f2)
    if [ ! -z "$GEMINI_KEY" ] && [ "$GEMINI_KEY" != "your-gemini-api-key-here" ]; then
        echo -e "${GREEN}✅ PASS${NC}: Gemini API key is set (${GEMINI_KEY:0:10}...)"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️  WARN${NC}: Gemini API key not set (optional feature)"
        ((WARN++))
    fi
fi

# Check 7: Frontend .env.local
echo ""
echo "7. Checking frontend environment..."
if [ -f "frontend/.env.local" ]; then
    echo -e "${GREEN}✅ PASS${NC}: frontend/.env.local exists"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  WARN${NC}: frontend/.env.local not found"
    echo "   Run: cd frontend && cp .env.example .env.local"
    ((WARN++))
fi

# Check 8: No hardcoded secrets in Python files
echo ""
echo "8. Scanning for hardcoded secrets in Python files..."
HARDCODED=$(grep -r "api_key\s*=\s*['\"][a-zA-Z0-9]\{20,\}['\"]" --include="*.py" . 2>/dev/null | grep -v ".env" | grep -v "venv/" | grep -v "__pycache__" || true)
if [ -z "$HARDCODED" ]; then
    echo -e "${GREEN}✅ PASS${NC}: No hardcoded API keys found in Python files"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}: Hardcoded API keys found:"
    echo "$HARDCODED"
    ((FAIL++))
fi

# Check 9: Database file security
echo ""
echo "9. Checking database file security..."
if [ -f "nasa_zeus.db" ]; then
    if grep -q "nasa_zeus.db" .gitignore || grep -q "*.db" .gitignore; then
        echo -e "${GREEN}✅ PASS${NC}: Database file is in .gitignore"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️  WARN${NC}: Database file should be in .gitignore"
        ((WARN++))
    fi
else
    echo -e "${GREEN}✅ PASS${NC}: No database file found yet"
    ((PASS++))
fi

# Check 10: CORS configuration
echo ""
echo "10. Checking CORS configuration..."
if grep -q 'allow_origins=\["*"\]' main.py || grep -q "\"*\"" main.py; then
    echo -e "${YELLOW}⚠️  WARN${NC}: CORS allows all origins (*)"
    echo "   For production, restrict to specific domains in main.py"
    ((WARN++))
else
    echo -e "${GREEN}✅ PASS${NC}: CORS is configured with specific origins"
    ((PASS++))
fi

# Summary
echo ""
echo "====================================="
echo "📊 Security Verification Summary"
echo "====================================="
echo -e "✅ Passed: ${GREEN}$PASS${NC}"
echo -e "❌ Failed: ${RED}$FAIL${NC}"
echo -e "⚠️  Warnings: ${YELLOW}$WARN${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical security checks passed!${NC}"
    if [ $WARN -gt 0 ]; then
        echo -e "${YELLOW}⚠️  But you have $WARN warnings to address${NC}"
    fi
    echo ""
    echo "✅ Your application is secure and ready for deployment!"
else
    echo -e "${RED}❌ You have $FAIL critical security issues to fix!${NC}"
    echo ""
    echo "🔧 Fix the issues above before deploying"
fi

echo ""
echo "📖 For deployment instructions, see: SECURITY_DEPLOYMENT_GUIDE.md"
echo ""
