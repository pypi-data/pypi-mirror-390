#!/bin/bash

# Time Doctor Scraper Installation Script

echo "=================================="
echo "Time Doctor Scraper - Installation"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if Python 3.10+
if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    echo "❌ Error: Python 3.10 or higher is required"
    echo "   Current version: $python_version"
    exit 1
fi

echo "✓ Python version OK"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo ""

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created from .env.example"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your Time Doctor credentials"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Create output directories
echo "Creating output directories..."
mkdir -p reports
mkdir -p logs
echo "✓ Output directories created"
echo ""

echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Time Doctor credentials:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the example script:"
echo "   python example.py"
echo ""
echo "4. Or start the MCP server:"
echo "   python src/mcp_server.py"
echo ""
echo "For more information, see README.md"
echo ""
