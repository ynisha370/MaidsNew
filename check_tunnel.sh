#!/bin/bash

# Check Cloudflare Tunnel Status
echo "🔍 Checking Cloudflare Tunnel Status..."
echo ""

# Check if cloudflared is running
if pgrep -f "cloudflared tunnel" > /dev/null; then
    echo "✅ Cloudflare tunnel is running!"
    echo ""
    echo "📋 Process details:"
    ps aux | grep cloudflared | grep -v grep
    echo ""
    echo "🌐 Your app should be accessible via the tunnel URL"
    echo "   (The URL is usually displayed when the tunnel starts)"
    echo ""
    echo "💡 To see the tunnel URL, check the terminal where you started the tunnel"
    echo "   or restart the tunnel to see the URL again"
else
    echo "❌ No Cloudflare tunnel is currently running"
    echo ""
    echo "🚀 To start a tunnel, run:"
    echo "   ./start_tunnel.sh"
fi
