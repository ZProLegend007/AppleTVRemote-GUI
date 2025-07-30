#!/bin/bash
# ApplerGUI Update Script

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$INSTALL_DIR/venv"

echo -e "${BLUE}🔄 Updating ApplerGUI...${NC}"

# Check if we're in the right directory
if [[ ! -f "$INSTALL_DIR/main.py" ]]; then
    echo -e "${RED}✗ Error: Not in ApplerGUI installation directory${NC}"
    exit 1
fi

# Check if virtual environment exists
if [[ ! -d "$VENV_DIR" ]]; then
    echo -e "${RED}✗ Error: Virtual environment not found${NC}"
    exit 1
fi

# Update from git
echo -e "${BLUE}→ Fetching latest changes...${NC}"
if git pull origin main; then
    echo -e "${GREEN}✓ Source code updated${NC}"
else
    echo -e "${YELLOW}⚠ Git pull failed, but continuing...${NC}"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Update dependencies
echo -e "${BLUE}→ Updating Python dependencies...${NC}"
if pip install --upgrade -r requirements.txt >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Dependencies updated${NC}"
else
    echo -e "${YELLOW}⚠ Some dependencies failed to update${NC}"
fi

# Run Qt connection check
echo -e "${BLUE}→ Checking Qt connections...${NC}"
if python3 qt_connection_fix.py >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Qt connections verified${NC}"
else
    echo -e "${YELLOW}⚠ Qt connection check had warnings${NC}"
fi

echo -e "${GREEN}✓ ApplerGUI update completed${NC}"