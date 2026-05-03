#!/bin/bash
# Dëkkal Gemini Integration — Setup Checklist
# Run this script to verify your setup

set -e  # Exit on error

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🌊 Dëkkal Gemini Integration — Setup Verification       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Google API Key
echo "📋 Check 1: Google API Key"
echo "─────────────────────────────────────────────────────────"

if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  GOOGLE_API_KEY not set${NC}"
    echo "   Get one from: https://aistudio.google.com/app/apikeys"
    echo "   Then run: export GOOGLE_API_KEY='your_key_here'"
    export GOOGLE_API_KEY="NOT_SET"
    CHECK_1=0
else
    echo -e "${GREEN}✅ GOOGLE_API_KEY is set${NC}"
    CHECK_1=1
fi
echo ""

# Check 2: Python Version
echo "📋 Check 2: Python Version"
echo "─────────────────────────────────────────────────────────"

PYTHON_VERSION=$(python --version 2>&1)
REQUIRED_VERSION="3.10"

if python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
    CHECK_2=1
else
    echo -e "${RED}❌ $PYTHON_VERSION (required >= 3.10)${NC}"
    CHECK_2=0
fi
echo ""

# Check 3: Backend directory
echo "📋 Check 3: Backend Directory Structure"
echo "─────────────────────────────────────────────────────────"

cd /home/seydina/dekkal/backend

FILES_TO_CHECK=(
    "main.py"
    "api/routers/score.py"
    "api/routers/batch_llm.py"
    "api/services/llm_explainer.py"
    "api/models/schemas.py"
    "pyproject.toml"
    ".env.example"
)

CHECK_3=1
for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}  ✅ $file${NC}"
    else
        echo -e "${RED}  ❌ $file (MISSING)${NC}"
        CHECK_3=0
    fi
done
echo ""

# Check 4: Required Python Packages
echo "📋 Check 4: Python Package Dependencies"
echo "─────────────────────────────────────────────────────────"

REQUIRED_PACKAGES=(
    "fastapi"
    "uvicorn"
    "pydantic"
    "google.generativeai"
    "requests"
    "scikit-learn"
)

CHECK_4=1
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import ${pkg/./}" 2>/dev/null; then
        echo -e "${GREEN}  ✅ $pkg${NC}"
    else
        echo -e "${YELLOW}  ⚠️  $pkg (not installed)${NC}"
        CHECK_4=0
    fi
done
echo ""

# Check 5: .env configuration
echo "📋 Check 5: Environment Configuration"
echo "─────────────────────────────────────────────────────────"

if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    if grep -q "GOOGLE_API_KEY" .env; then
        echo -e "${GREEN}   ✅ GOOGLE_API_KEY configured${NC}"
        CHECK_5=1
    else
        echo -e "${YELLOW}   ⚠️  GOOGLE_API_KEY not in .env${NC}"
        CHECK_5=0
    fi
else
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}⚠️  .env file not found (but .env.example exists)${NC}"
        echo "   Run: cp .env.example .env"
        echo "   Then: edit .env and add your GOOGLE_API_KEY"
        CHECK_5=0
    else
        echo -e "${RED}❌ .env.example not found${NC}"
        CHECK_5=0
    fi
fi
echo ""

# Check 6: Port availability
echo "📋 Check 6: Port 8000 Availability"
echo "─────────────────────────────────────────────────────────"

if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Port 8000 is available${NC}"
    CHECK_6=1
else
    echo -e "${YELLOW}⚠️  Port 8000 is in use${NC}"
    echo "   Either stop the service using it or use a different port:"
    echo "   python -m uvicorn main:app --port 9000"
    CHECK_6=0
fi
echo ""

# Summary
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                     SUMMARY                              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

TOTAL=$((CHECK_1 + CHECK_2 + CHECK_3 + CHECK_4 + CHECK_5 + CHECK_6))
PASSED=0

echo "Checks:"
[ $CHECK_1 -eq 1 ] && echo -e "${GREEN}  ✅ Google API Key${NC}" || echo -e "${RED}  ❌ Google API Key${NC}"
[ $CHECK_2 -eq 1 ] && echo -e "${GREEN}  ✅ Python Version${NC}" || echo -e "${RED}  ❌ Python Version${NC}"
[ $CHECK_3 -eq 1 ] && echo -e "${GREEN}  ✅ Backend Files${NC}" || echo -e "${RED}  ❌ Backend Files${NC}"
[ $CHECK_4 -eq 1 ] && echo -e "${GREEN}  ✅ Python Packages${NC}" || echo -e "${YELLOW}  ⚠️  Python Packages${NC}"
[ $CHECK_5 -eq 1 ] && echo -e "${GREEN}  ✅ Configuration${NC}" || echo -e "${RED}  ❌ Configuration${NC}"
[ $CHECK_6 -eq 1 ] && echo -e "${GREEN}  ✅ Port Available${NC}" || echo -e "${YELLOW}  ⚠️  Port Available${NC}"

echo ""
echo "─────────────────────────────────────────────────────────"
echo ""

# Next steps
if [ $CHECK_1 -eq 0 ] || [ $CHECK_5 -eq 0 ]; then
    echo -e "${RED}⚠️  SETUP INCOMPLETE${NC}"
    echo ""
    echo "Required actions:"
    if [ $CHECK_1 -eq 0 ]; then
        echo "  1. Get your Google API Key:"
        echo "     → https://aistudio.google.com/app/apikeys"
        echo "     → export GOOGLE_API_KEY='your_key_here'"
    fi
    if [ $CHECK_5 -eq 0 ]; then
        echo "  2. Configure .env file:"
        echo "     → cp .env.example .env"
        echo "     → Add your GOOGLE_API_KEY to .env"
    fi
else
    echo -e "${GREEN}✅ SETUP COMPLETE!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Install missing packages (if any):"
    echo "     pip install -r requirements.txt"
    echo ""
    echo "  2. Start the API server:"
    echo "     python -m uvicorn main:app --reload --port 8000"
    echo ""
    echo "  3. In another terminal, test the API:"
    echo "     python test_gemini_integration.py"
    echo ""
    echo "  4. Or run examples:"
    echo "     python examples_gemini.py"
    echo ""
    echo "  5. View API docs:"
    echo "     http://localhost:8000/docs"
fi

echo ""
echo "─────────────────────────────────────────────────────────"
echo "Documentation:"
echo "  • Full guide: ./GEMINI_INTEGRATION.md"
echo "  • Quick start: ./QUICK_START_GEMINI.md"
echo "  • Examples: ./examples_gemini.py"
echo "─────────────────────────────────────────────────────────"
echo ""
