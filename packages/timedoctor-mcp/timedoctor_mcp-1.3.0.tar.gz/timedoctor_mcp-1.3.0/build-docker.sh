#!/bin/bash

# Build Docker Image for Time Doctor MCP Server

echo "=========================================="
echo "Building Time Doctor MCP Server (Docker)"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo ""
    echo "Please start Docker Desktop:"
    echo "  open -a Docker"
    echo ""
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo ""
    echo "You'll need to create .env with:"
    echo "  TD_EMAIL=your-email@example.com"
    echo "  TD_PASSWORD=your-password"
    echo ""
fi

# Build the image
echo "Building Docker image..."
echo "This may take a few minutes (installing Playwright and Chromium)..."
echo ""

docker build -t timedoctor-scraper:latest .

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Docker image built successfully!"
    echo "=========================================="
    echo ""
    echo "Image: timedoctor-scraper:latest"
    echo ""

    # Show image size
    SIZE=$(docker images timedoctor-scraper:latest --format "{{.Size}}")
    echo "Size: $SIZE"
    echo ""

    echo "Next steps:"
    echo ""
    echo "1. Test the Docker setup:"
    echo "   ./docker-mcp-wrapper.sh"
    echo ""
    echo "2. Add to Claude Desktop config:"
    echo "   open ~/Library/Application\ Support/Claude/claude_desktop_config.json"
    echo ""
    echo "   Add this:"
    echo '   {'
    echo '     "mcpServers": {'
    echo '       "timedoctor": {'
    echo '         "command": "/Users/apple/tdoctorscraper/docker-mcp-wrapper.sh",'
    echo '         "args": []'
    echo '       }'
    echo '     }'
    echo '   }'
    echo ""
    echo "3. Restart Claude Desktop"
    echo ""
    echo "4. Test: 'Get my Time Doctor report for today'"
    echo ""
    echo "=========================================="
else
    echo ""
    echo "❌ Build failed!"
    echo ""
    echo "Check the error messages above."
    echo ""
    exit 1
fi
