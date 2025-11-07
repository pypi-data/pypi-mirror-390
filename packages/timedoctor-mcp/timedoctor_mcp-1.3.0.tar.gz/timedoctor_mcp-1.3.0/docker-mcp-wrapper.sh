#!/bin/bash

# Docker MCP Wrapper Script
# This script allows Claude Desktop to use the Time Doctor scraper via Docker

# Load environment from .env file
if [ -f "$(dirname "$0")/.env" ]; then
    export $(cat "$(dirname "$0")/.env" | grep -v '^#' | xargs)
fi

# Run the MCP server in Docker with stdio
docker run -i --rm \
    -e TD_EMAIL="$TD_EMAIL" \
    -e TD_PASSWORD="$TD_PASSWORD" \
    -e TD_BASE_URL="${TD_BASE_URL:-https://2.timedoctor.com}" \
    -e HEADLESS="${HEADLESS:-true}" \
    -e BROWSER_TIMEOUT="${BROWSER_TIMEOUT:-60000}" \
    -e LOG_LEVEL="${LOG_LEVEL:-INFO}" \
    -v "$(dirname "$0")/output:/app/output" \
    timedoctor-scraper:latest \
    python src/mcp_server.py
