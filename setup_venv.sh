#!/bin/bash

# ADK Voice Agent - Virtual Environment Setup Script
# This script creates a virtual environment and installs all required dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_NAME="venv"
PYTHON_CMD="python3"
REQUIREMENTS_FILE="requirements.txt"

echo -e "${BLUE}🚀 ADK Voice Agent - Environment Setup${NC}"
echo "==========================================="

# Check if Python is available
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}❌ Error: $PYTHON_CMD is not installed or not in PATH${NC}"
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Display Python version
PYTHON_VERSION=$($PYTHON_CMD --version)
echo -e "${BLUE}🐍 Using: $PYTHON_VERSION${NC}"

# Check if requirements.txt exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${RED}❌ Error: $REQUIREMENTS_FILE not found in current directory${NC}"
    exit 1
fi

# Check if virtual environment already exists
if [ -d "$VENV_NAME" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment '$VENV_NAME' already exists${NC}"
    read -p "Do you want to remove it and create a new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🗑️  Removing existing virtual environment...${NC}"
        rm -rf "$VENV_NAME"
    else
        echo -e "${BLUE}ℹ️  Using existing virtual environment${NC}"
        source "$VENV_NAME/bin/activate"
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
        echo -e "${BLUE}📦 Installing/updating packages from requirements.txt...${NC}"
        pip install --upgrade pip
        pip install -r "$REQUIREMENTS_FILE"
        echo -e "${GREEN}✅ Setup complete!${NC}"
        echo ""
        echo -e "${BLUE}🎯 Next steps:${NC}"
        echo "1. Activate the virtual environment: source $VENV_NAME/bin/activate"
        echo "2. Set up your .env file with required API keys"
        echo "3. Run the application: uvicorn app.main:app --reload"
        exit 0
    fi
fi

# Create virtual environment
echo -e "${BLUE}📁 Creating virtual environment '$VENV_NAME'...${NC}"
$PYTHON_CMD -m venv "$VENV_NAME"

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source "$VENV_NAME/bin/activate"

# Verify activation
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✅ Virtual environment activated: $VIRTUAL_ENV${NC}"
else
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

# Upgrade pip
echo -e "${BLUE}⬆️  Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${BLUE}📦 Installing packages from $REQUIREMENTS_FILE...${NC}"
echo "This may take a few minutes..."
pip install -r "$REQUIREMENTS_FILE"

# Verify installation
echo -e "${BLUE}🔍 Verifying installation...${NC}"
pip list | head -10

echo ""
echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo "==========================================="
echo -e "${BLUE}🎯 Next steps:${NC}"
echo ""
echo "1. Activate the virtual environment (when needed):"
echo -e "   ${YELLOW}source $VENV_NAME/bin/activate${NC}"
echo ""
echo "2. Make sure you have a .env file with your API keys:"
echo -e "   ${YELLOW}cp .env.example .env  # if you have an example file${NC}"
echo -e "   ${YELLOW}# Add your GOOGLE_API_KEY and other required variables${NC}"
echo ""
echo "3. Run the FastAPI application:"
echo -e "   ${YELLOW}uvicorn app.main:app --reload${NC}"
echo ""
echo "4. Deactivate when done:"
echo -e "   ${YELLOW}deactivate${NC}"
echo ""
echo -e "${BLUE}📝 Notes:${NC}"
echo "- Virtual environment created in: ./$VENV_NAME"
echo "- Requirements installed from: ./$REQUIREMENTS_FILE"
echo "- The application will be available at: http://localhost:8000"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
