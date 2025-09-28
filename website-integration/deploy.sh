#!/bin/bash

# Islamic AI Agent Deployment Script
# This script helps deploy your Islamic AI backend for website integration

echo "🕌 Islamic AI Agent Deployment Script"
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

print_status "Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi

print_status "pip3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "islamic_ai_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv islamic_ai_env
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source islamic_ai_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    print_status "Requirements installed"
else
    print_warning "requirements.txt not found. Installing basic dependencies..."
    pip install flask flask-cors requests agentscope google-generativeai openai
fi

# Check for API keys
echo ""
echo "🔑 Checking API Keys..."

if [ -z "$GOOGLE_API_KEY" ]; then
    print_warning "GOOGLE_API_KEY environment variable not set"
    echo "Please set your Google Gemini API key:"
    echo "export GOOGLE_API_KEY='your-gemini-api-key'"
else
    print_status "Google API key found"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    print_warning "OPENAI_API_KEY environment variable not set"
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY='your-openai-api-key'"
else
    print_status "OpenAI API key found"
fi

# Check if main files exist
echo ""
echo "📁 Checking required files..."

required_files=("simple_api.py" "multi_agent_islamic_system.py" "islamic_ai_agent.py")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "$file found"
    else
        print_error "$file not found"
        exit 1
    fi
done

# Create production configuration
echo ""
echo "⚙️  Creating production configuration..."

cat > production_config.py << EOF
# Production Configuration for Islamic AI Agent
import os

class ProductionConfig:
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5002))
    DEBUG = False
    
    # CORS Configuration
    CORS_ORIGINS = [
        'https://theislaminsights.com',
        'https://www.theislaminsights.com'
    ]
    
    # API Keys (from environment variables)
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = '100 per hour'
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

config = ProductionConfig()
EOF

print_status "Production configuration created"

# Create startup script
echo ""
echo "🚀 Creating startup script..."

cat > start_server.sh << 'EOF'
#!/bin/bash

# Islamic AI Agent Server Startup Script

echo "🕌 Starting Islamic AI Agent Server..."

# Activate virtual environment
source islamic_ai_env/bin/activate

# Set production environment
export FLASK_ENV=production

# Check API keys
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ GOOGLE_API_KEY not set. Please set your Gemini API key."
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not set. Please set your OpenAI API key."
    exit 1
fi

# Start the server
echo "✅ Starting server on port ${PORT:-5002}..."
python simple_api.py

EOF

chmod +x start_server.sh
print_status "Startup script created (start_server.sh)"

# Create systemd service file (for Linux servers)
echo ""
echo "🔧 Creating systemd service file..."

cat > islamic-ai-agent.service << EOF
[Unit]
Description=Islamic AI Agent API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/islamic_ai_env/bin
Environment=GOOGLE_API_KEY=your-gemini-api-key
Environment=OPENAI_API_KEY=your-openai-api-key
ExecStart=$(pwd)/islamic_ai_env/bin/python simple_api.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

print_status "Systemd service file created (islamic-ai-agent.service)"

# Create nginx configuration
echo ""
echo "🌐 Creating nginx configuration..."

cat > nginx-islamic-ai.conf << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration (update paths to your certificates)
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin "https://theislaminsights.com";
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
    }
    
    # Handle preflight requests
    location ~ ^/api/ {
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin "https://theislaminsights.com";
            add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type, Authorization";
            add_header Access-Control-Max-Age 86400;
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 204;
        }
        
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

print_status "Nginx configuration created (nginx-islamic-ai.conf)"

# Create Docker configuration
echo ""
echo "🐳 Creating Docker configuration..."

cat > Dockerfile << 'EOF'
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 5002

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "simple_api.py"]
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  islamic-ai-agent:
    build: .
    ports:
      - "5002:5002"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FLASK_ENV=production
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF

print_status "Docker configuration created"

# Create environment file template
echo ""
echo "📝 Creating environment file template..."

cat > .env.example << 'EOF'
# Islamic AI Agent Environment Variables
# Copy this file to .env and fill in your actual values

# Required API Keys
GOOGLE_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Server Configuration
PORT=5002
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this

# Optional: Database URL (if using database)
# DATABASE_URL=postgresql://user:password@localhost/islamic_ai

# Optional: Redis URL (for caching)
# REDIS_URL=redis://localhost:6379
EOF

print_status "Environment file template created (.env.example)"

# Final instructions
echo ""
echo "🎉 Deployment setup complete!"
echo ""
echo "📋 Next Steps:"
echo "=============="
echo ""
echo "1. 🔑 Set your API keys:"
echo "   export GOOGLE_API_KEY='your-gemini-api-key'"
echo "   export OPENAI_API_KEY='your-openai-api-key'"
echo ""
echo "2. 🧪 Test locally:"
echo "   ./start_server.sh"
echo ""
echo "3. 🌐 For production deployment, choose one:"
echo ""
echo "   📦 Docker (Recommended):"
echo "   - Copy .env.example to .env and fill in your keys"
echo "   - Run: docker-compose up -d"
echo ""
echo "   🖥️  Traditional Server:"
echo "   - Copy islamic-ai-agent.service to /etc/systemd/system/"
echo "   - Update the service file with your paths and API keys"
echo "   - Run: sudo systemctl enable islamic-ai-agent"
echo "   - Run: sudo systemctl start islamic-ai-agent"
echo ""
echo "   🌐 Nginx (for HTTPS):"
echo "   - Copy nginx-islamic-ai.conf to /etc/nginx/sites-available/"
echo "   - Update server_name and SSL certificate paths"
echo "   - Enable: sudo ln -s /etc/nginx/sites-available/nginx-islamic-ai.conf /etc/nginx/sites-enabled/"
echo "   - Restart: sudo systemctl restart nginx"
echo ""
echo "4. 🔗 Update your website:"
echo "   - Upload islamic-chat-widget.js to your website"
echo "   - Add the widget code to theislaminsights.com"
echo "   - Update apiUrl to your deployed server URL"
echo ""
echo "5. ✅ Test the integration:"
echo "   - Visit theislaminsights.com"
echo "   - Click the chat button"
echo "   - Test all 4 search modes"
echo ""
echo "🆘 Need help? Check the WEBSITE_INTEGRATION_GUIDE.md for detailed instructions."
echo ""
print_status "Islamic AI Agent is ready for deployment! 🕌"

EOF

chmod +x deploy.sh
