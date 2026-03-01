#!/bin/bash
# MedObsMind Production Deployment Script
# Domain: MedObsMind.in

set -e

echo "=========================================="
echo "  MedObsMind Production Installer"
echo "  Domain: MedObsMind.in"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS. Please install manually."
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker $SUDO_USER || true
    systemctl enable docker
    systemctl start docker
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Clone repository
echo "Cloning MedObsMind repository..."
cd /opt
if [ -d "MedObsMind" ]; then
    echo "Repository already exists, pulling latest..."
    cd MedObsMind
    git pull
else
    git clone https://github.com/Sharmapank-j/MedObsMind.git
    cd MedObsMind
fi
echo "✅ Repository ready"

# Setup environment
echo "Setting up environment..."
if [ ! -f .env ]; then
    cp .env.production.example .env
    
    # Generate random secrets
    SECRET_KEY=$(openssl rand -hex 32)
    POSTGRES_PASSWORD=$(openssl rand -hex 16)
    REDIS_PASSWORD=$(openssl rand -hex 16)
    
    # Replace placeholders
    sed -i "s/change-this-to-a-random-secret-key-at-least-50-characters-long/$SECRET_KEY/g" .env
    sed -i "s/change-this-secure-password/$POSTGRES_PASSWORD/g" .env
    sed -i "s/change-this-redis-password/$REDIS_PASSWORD/g" .env
    
    echo "✅ Environment file created with secure passwords"
    echo ""
    echo "⚠️  IMPORTANT: Configure these in .env:"
    echo "    - GOOGLE_CLIENT_ID"
    echo "    - GOOGLE_CLIENT_SECRET"
    echo "    - EMAIL settings (for notifications)"
    echo ""
else
    echo "✅ Environment file exists"
fi

# Create necessary directories
mkdir -p nginx/ssl backup models

# Deploy with Docker Compose
echo "Deploying MedObsMind..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 15

# Check health
echo "Checking service health..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "=========================================="
echo "  ✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "MedObsMind is now running!"
echo ""
echo "Server IP: $(hostname -I | awk '{print $1}')"
echo ""
echo "Access (via IP for now):"
echo "  - Website: http://$(hostname -I | awk '{print $1}')"
echo "  - API: http://$(hostname -I | awk '{print $1}')/api"
echo "  - Admin: http://$(hostname -I | awk '{print $1}')/admin"
echo ""
echo "Domain Configuration (MedObsMind.in):"
echo "  1. Point DNS A records to: $(hostname -I | awk '{print $1}')"
echo "     - medobsmind.in → $(hostname -I | awk '{print $1}')"
echo "     - www.medobsmind.in → $(hostname -I | awk '{print $1}')"
echo "     - api.medobsmind.in → $(hostname -I | awk '{print $1}')"
echo ""
echo "  2. Install SSL certificate:"
echo "     sudo apt install certbot python3-certbot-nginx"
echo "     sudo certbot --nginx -d medobsmind.in -d www.medobsmind.in -d api.medobsmind.in"
echo ""
echo "Next steps:"
echo "  3. Create admin user:"
echo "     cd /opt/MedObsMind"
echo "     docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser"
echo ""
echo "  4. Download AI models:"
echo "     docker-compose -f docker-compose.prod.yml exec backend python scripts/download_model.py"
echo ""
echo "Documentation: https://github.com/Sharmapank-j/MedObsMind/blob/main/DEPLOYMENT_GUIDE.md"
echo ""
echo "🎉 Welcome to MedObsMind!"
echo ""
