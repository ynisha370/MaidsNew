#!/bin/bash

# Cloudflare Tunnel Script for Port 3000
# This script creates a temporary tunnel to expose your React app

echo "🚀 Starting Cloudflare Tunnel for port 3000..."
echo "📱 Make sure your React app is running on http://localhost:3000"
echo ""

# Check if port 3000 is in use
if ! lsof -i :3000 > /dev/null 2>&1; then
    echo "⚠️  Warning: Nothing seems to be running on port 3000"
    echo "   Start your React app first with: cd frontend && npm start"
    echo ""
fi

echo "🔗 Creating temporary tunnel..."
echo "   This will give you a public URL to access your app"
echo ""

# Start the tunnel
cloudflared tunnel --url http://localhost:3000
