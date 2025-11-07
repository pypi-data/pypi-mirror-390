# Time Doctor Scraper - MCP Server
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy source code
COPY src/ ./src/

# Set environment variables (will be overridden by docker-compose or run command)
ENV TD_EMAIL=""
ENV TD_PASSWORD=""
ENV TD_BASE_URL="https://2.timedoctor.com"
ENV HEADLESS="true"
ENV BROWSER_TIMEOUT="60000"
ENV LOG_LEVEL="INFO"

# Run MCP server
CMD ["python", "src/mcp_server.py"]
