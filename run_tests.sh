#!/bin/bash

set -e  # Exit on any error

echo "🧪 Running Monopoly Deal Test Suite"
echo "=================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}📝 Code Quality Checks${NC}"
echo "--------------------"

# 1. Black formatting check
echo -e "${YELLOW}Running Black formatting check...${NC}"
if black --check .; then
    echo -e "${GREEN}✅ Black formatting check passed${NC}"
else
    echo -e "${RED}❌ Black formatting check failed${NC}"
    exit 1
fi

# 2. Flake8 linting  
echo -e "${YELLOW}Running Flake8 linting...${NC}"
if flake8 --max-line-length=88 .; then
    echo -e "${GREEN}✅ Flake8 linting passed${NC}"
else
    echo -e "${RED}❌ Flake8 linting failed${NC}"
    exit 1
fi

# 3. Prettier formatting check
echo -e "${YELLOW}Running Prettier formatting check...${NC}"
if command -v prettier >/dev/null 2>&1; then
    if prettier --check "**/*.{html,css,js}" 2>/dev/null; then
        echo -e "${GREEN}✅ Prettier formatting check passed${NC}"
    else
        echo -e "${RED}❌ Prettier formatting check failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Prettier not available - skipping formatting check${NC}"
fi

# 4. Python class detection check
echo -e "${YELLOW}Checking for Python class definitions...${NC}"
if grep -RInE \
    --include='*.py' \
    --exclude-dir={.git,venv,.venv,node_modules,dist,build,.mypy_cache,.pytest_cache} \
    '^[[:space:]]*class[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*(\(|:)' \
    . >/dev/null 2>&1; then
    echo -e "${RED}❌ Python class definitions found in the codebase!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ No Python classes found - function-based architecture maintained${NC}"
fi

echo ""
echo -e "${BLUE}🧪 Python Test Suite${NC}"
echo "-------------------"

# 5. Run FastAPI tests
echo -e "${YELLOW}Running FastAPI tests...${NC}"
if python test_fastapi.py; then
    echo -e "${GREEN}✅ FastAPI tests passed${NC}"
else
    echo -e "${RED}❌ FastAPI tests failed${NC}"
    exit 1
fi

# 6. Run Lobby tests
echo -e "${YELLOW}Running Lobby tests...${NC}"
if python test_lobby.py; then
    echo -e "${GREEN}✅ Lobby tests passed${NC}"
else
    echo -e "${RED}❌ Lobby tests failed${NC}"
    exit 1
fi

# 7. Run Database tests (allow failure since DB may not be available)
echo -e "${YELLOW}Running Database tests...${NC}"
if python test_database.py; then
    echo -e "${GREEN}✅ Database tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  Database tests failed (expected if PostgreSQL not available)${NC}"
    # Don't exit on database test failure since PostgreSQL may not be running
fi

echo ""
echo -e "${GREEN}🎉 All tests completed successfully!${NC}"
echo "=================================="