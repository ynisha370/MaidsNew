#!/bin/bash

# Maids of CyFair - Service Startup Script
# This script starts the frontend, backend, and nginx services

set -e

echo "🚀 Starting Maids of CyFair Services..."

# Create logs directory if it doesn't exist
mkdir -p /root/MaidsNew/logs

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2 is not installed. Installing PM2..."
    npm install -g pm2
fi

# Check if Nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx is not installed. Installing Nginx..."
    apt-get update
    apt-get install -y nginx
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd /root/MaidsNew/backend
pip3 install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd /root/MaidsNew/frontend
npm install

# Stop any existing PM2 processes
echo "🛑 Stopping existing PM2 processes..."
pm2 stop all 2>/dev/null || true
pm2 delete all 2>/dev/null || true

# Start services with PM2
echo "🚀 Starting services with PM2..."
cd /root/MaidsNew
pm2 start ecosystem.config.js --env production

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup

# Start Nginx
echo "🌐 Starting Nginx..."
systemctl start nginx
systemctl enable nginx

# Copy Nginx configuration
cp /root/MaidsNew/nginx.conf /etc/nginx/sites-available/maids-of-cyfair
ln -sf /etc/nginx/sites-available/maids-of-cyfair /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Reload Nginx
systemctl reload nginx

echo "✅ All services started successfully!"
echo ""
echo "📊 Service Status:"
pm2 status
echo ""
echo "🌐 Services are available at:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost/api"
echo ""
echo "📝 Logs:"
echo "   PM2 logs: pm2 logs"
echo "   Nginx logs: tail -f /var/log/nginx/access.log"
echo "   Application logs: tail -f /root/MaidsNew/logs/*.log"

