#!/bin/bash
# Quick Deploy Script - Run this to deploy MedObsMind
# Usage: bash DEPLOY_NOW.sh

echo "=========================================="
echo "  MedObsMind Quick Deploy"
echo "  Domain: MedObsMind.in"
echo "=========================================="
echo ""

# Check if on server or local
if [ ! -f "/etc/hostname" ] || ! ping -c 1 google.com > /dev/null 2>&1; then
    echo "⚠️  This should be run on your production server"
    echo ""
    echo "To deploy:"
    echo "1. SSH into your server: ssh user@your-server-ip"
    echo "2. Run this command:"
    echo ""
    echo "   curl -fsSL https://raw.githubusercontent.com/Sharmapank-j/MedObsMind/main/scripts/deploy.sh | sudo bash"
    echo ""
    exit 0
fi

# Check if already deployed
if [ -d "/opt/MedObsMind" ]; then
    echo "✅ MedObsMind is already deployed at /opt/MedObsMind"
    echo ""
    echo "To update:"
    echo "  cd /opt/MedObsMind"
    echo "  git pull"
    echo "  docker-compose -f docker-compose.prod.yml up -d --build"
    echo ""
    exit 0
fi

# Run deployment
echo "🚀 Starting deployment..."
echo ""

curl -fsSL https://raw.githubusercontent.com/Sharmapank-j/MedObsMind/main/scripts/deploy.sh | sudo bash

echo ""
echo "=========================================="
echo "  ✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure DNS (see DNS_SETUP.md)"
echo "2. Install SSL certificate"
echo "3. Create admin user"
echo "4. Access: http://$(hostname -I | awk '{print $1}')"
echo ""
