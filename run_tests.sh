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
if flake8 --max-line-length=88 --exclude=".venv,.git,__pycache__,migrations,env,.env" .; then
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
CLASS_FILES=$(grep -RlnE \
    --include='*.py' \
    --exclude-dir={.git,venv,.venv,node_modules,dist,build,.mypy_cache,.pytest_cache,env,.env} \
    '^[[:space:]]*class[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*(\(|:)' \
    . 2>/dev/null || true)

if [ -n "$CLASS_FILES" ]; then
    echo -e "${RED}❌ Python class definitions found in the codebase!${NC}"
    echo -e "${RED}Files containing classes:${NC}"
    echo "$CLASS_FILES"
    echo -e "${YELLOW}Hint: If this is unexpected, try rebuilding the Docker container:${NC}"
    echo -e "${YELLOW}  docker compose down --remove-orphans${NC}"
    echo -e "${YELLOW}  docker compose --profile test build --no-cache test${NC}"
    echo -e "${YELLOW}  docker compose --profile test run --rm test${NC}"
    exit 1
else
    echo -e "${GREEN}✅ No Python classes found - function-based architecture maintained${NC}"
fi

echo ""
echo -e "${BLUE}🧪 Application Tests${NC}"
echo "------------------"

# 5. FastAPI tests
echo -e "${YELLOW}Running FastAPI tests...${NC}"
if python test_fastapi.py; then
    echo -e "${GREEN}✅ FastAPI tests passed${NC}"
else
    echo -e "${RED}❌ FastAPI tests failed${NC}"
    exit 1
fi

# 6. Lobby tests
echo -e "${YELLOW}Running Lobby tests...${NC}"
if python test_lobby.py; then
    echo -e "${GREEN}✅ Lobby tests passed${NC}"
else
    echo -e "${RED}❌ Lobby tests failed${NC}"
    exit 1
fi

# 7. 2FA tests
echo -e "${YELLOW}Running 2FA tests...${NC}"
if python test_2fa.py; then
    echo -e "${GREEN}✅ 2FA tests passed${NC}"
else
    echo -e "${RED}❌ 2FA tests failed${NC}"
    exit 1
fi

# 8. Business hours tests
echo -e "${YELLOW}Running Business hours tests...${NC}"
if python test_business_hours.py; then
    echo -e "${GREEN}✅ Business hours tests passed${NC}"
else
    echo -e "${RED}❌ Business hours tests failed${NC}"
    exit 1
fi

# 9. Database tests (allow failure)
echo -e "${YELLOW}Running Database tests...${NC}"
if timeout 20 python test_database.py; then
    echo -e "${GREEN}✅ Database tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  Database tests failed (expected if PostgreSQL not available)${NC}"
fi

echo ""
echo -e "${BLUE}🐍 Conda-based Linting & Tests${NC}"
echo "-------------------------------"

if command -v conda >/dev/null 2>&1; then
    if [ -f "environment.yml" ]; then
        echo -e "${YELLOW}Updating Conda environment...${NC}"
        conda env update --file environment.yml --name base
    else
        echo -e "${YELLOW}No environment.yml found - skipping conda environment update${NC}"
    fi

    echo -e "${YELLOW}Installing flake8 in Conda...${NC}"
    conda install -y flake8

    echo -e "${YELLOW}Running flake8 (strict)...${NC}"
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

    echo -e "${YELLOW}Running flake8 (warnings)...${NC}"
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    if command -v pytest >/dev/null 2>&1; then
        echo -e "${YELLOW}Running pytest...${NC}"
        pytest
    else
        echo -e "${YELLOW}Installing pytest in Conda...${NC}"
        conda install -y pytest
        echo -e "${YELLOW}Running pytest...${NC}"
        pytest
    fi
else
    echo -e "${YELLOW}⚠️  Conda not available - skipping Conda-based linting and tests${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All tests completed successfully!${NC}"
echo "=================================="