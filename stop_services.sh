#!/bin/bash

# Maids of CyFair - Service Stop Script
# This script stops all services

set -e

echo "🛑 Stopping Maids of CyFair Services..."

# Stop PM2 processes
echo "🛑 Stopping PM2 processes..."
pm2 stop all 2>/dev/null || true
pm2 delete all 2>/dev/null || true

# Stop Nginx
echo "🌐 Stopping Nginx..."
systemctl stop nginx 2>/dev/null || true

echo "✅ All services stopped successfully!"

