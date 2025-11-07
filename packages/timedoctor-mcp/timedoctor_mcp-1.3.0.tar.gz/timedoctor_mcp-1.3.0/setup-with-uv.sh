#!/bin/bash
# Setup Time Doctor Scraper with UV

echo "╔════════════════════════════════════════════╗"
echo "║   Time Doctor Scraper - UV Setup          ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV..."
    brew install uv
    echo "✅ UV installed"
else
    echo "✅ UV already installed"
fi

echo ""
echo "🧹 Cleaning old virtual environments..."
rm -rf venv .venv

echo ""
echo "🐍 Checking Python versions..."

# Try to use Python 3.13 if available, otherwise use system Python
if command -v python3.13 &> /dev/null; then
    echo "✅ Found Python 3.13"
    PYTHON_VERSION="3.13"
elif command -v python3.12 &> /dev/null; then
    echo "✅ Found Python 3.12"
    PYTHON_VERSION="3.12"
else
    echo "⚠️  Python 3.12/3.13 not found, will try with system Python"
    PYTHON_VERSION=""
fi

echo ""
echo "🔧 Creating virtual environment with UV..."
if [ -n "$PYTHON_VERSION" ]; then
    uv venv --python $PYTHON_VERSION
else
    uv venv
fi

echo ""
echo "📂 Activating virtual environment..."
source .venv/bin/activate

echo ""
echo "📦 Installing dependencies with UV (this is fast!)..."
uv pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Installation failed!"
    echo ""
    echo "The issue is likely Python 3.14 compatibility."
    echo "Please install Python 3.13:"
    echo ""
    echo "  brew install python@3.13"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo ""
echo "🎭 Installing Playwright browsers..."
playwright install chromium

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║         Installation Complete! ✅          ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Configure credentials:"
echo "   nano .env"
echo "   (Set TD_EMAIL and TD_PASSWORD)"
echo ""
echo "2️⃣  Activate environment:"
echo "   source .venv/bin/activate"
echo ""
echo "3️⃣  Test the scraper:"
echo "   python example.py"
echo ""
echo "4️⃣  Or start MCP server:"
echo "   python src/mcp_server.py"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Full documentation"
echo "   - QUICKSTART.md - Quick start guide"
echo "   - INSTALL_WITH_UV.md - UV installation guide"
echo ""
