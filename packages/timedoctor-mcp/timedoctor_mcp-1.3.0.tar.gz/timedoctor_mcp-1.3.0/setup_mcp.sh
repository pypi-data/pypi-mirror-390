#!/bin/bash

# Time Doctor MCP Server Setup Script
# This script helps you configure Claude Desktop to use Time Doctor scraper

echo "=========================================="
echo "Time Doctor MCP Server Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Please create .env with your credentials:"
    echo ""
    echo "TD_EMAIL=your-email@example.com"
    echo "TD_PASSWORD=your-password"
    echo "TD_BASE_URL=https://2.timedoctor.com"
    echo "HEADLESS=true"
    echo ""
    exit 1
fi

# Read credentials from .env
source .env

echo "✓ Found .env file"
echo "  Email: $TD_EMAIL"
echo ""

# Claude Desktop config path
CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

echo "Claude Desktop config location:"
echo "$CONFIG_PATH"
echo ""

# Check if config exists
if [ ! -f "$CONFIG_PATH" ]; then
    echo "⚠️  Claude Desktop config not found!"
    echo "Creating new config file..."
    mkdir -p "$HOME/Library/Application Support/Claude"
    echo '{}' > "$CONFIG_PATH"
fi

# Get absolute path to this directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_PATH="$PROJECT_DIR/.venv/bin/python"

# Create MCP config
cat > /tmp/timedoctor_mcp_config.json <<EOF
{
  "mcpServers": {
    "timedoctor": {
      "command": "$PYTHON_PATH",
      "args": [
        "$PROJECT_DIR/src/mcp_server.py"
      ],
      "env": {
        "TD_EMAIL": "$TD_EMAIL",
        "TD_PASSWORD": "$TD_PASSWORD",
        "TD_BASE_URL": "${TD_BASE_URL:-https://2.timedoctor.com}",
        "HEADLESS": "${HEADLESS:-true}"
      }
    }
  }
}
EOF

echo "Generated MCP configuration:"
echo ""
cat /tmp/timedoctor_mcp_config.json
echo ""
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Copy the configuration above"
echo "2. Open Claude Desktop config:"
echo "   open '$CONFIG_PATH'"
echo ""
echo "3. Add the 'timedoctor' server to your mcpServers section"
echo ""
echo "4. Restart Claude Desktop"
echo ""
echo "5. Test with: 'Get my Time Doctor report for today'"
echo ""
echo "=========================================="
echo ""
echo "Or, to automatically add it:"
echo "  ./setup_mcp.sh --auto"
echo ""
