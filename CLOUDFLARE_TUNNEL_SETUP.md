# Cloudflare Tunnel Setup for Port 3000

This guide helps you expose your React app (running on port 3000) to the internet using Cloudflare Tunnel.

## Quick Start (Temporary Tunnel)

### Option 1: One-time Temporary Tunnel
```bash
# Start your React app first
cd frontend
npm start

# In another terminal, create a temporary tunnel
cloudflared tunnel --url http://localhost:3000
```

### Option 2: Using the Helper Scripts
```bash
# Make sure your React app is running on port 3000
cd frontend && npm start

# In another terminal, start the tunnel
./start_tunnel.sh

# Check tunnel status
./check_tunnel.sh
```

## What You'll Get

- A public URL like `https://random-subdomain.trycloudflare.com`
- Your React app accessible from anywhere on the internet
- No need to configure firewalls or port forwarding
- HTTPS encryption automatically provided

## Prerequisites

1. **React App Running**: Make sure your frontend is running on port 3000
   ```bash
   cd frontend
   npm start
   ```

2. **Cloudflared Installed**: Already installed via Homebrew
   ```bash
   brew install cloudflared
   ```

## Authentication (First Time Only)

If this is your first time using cloudflared, you'll need to authenticate:

```bash
cloudflared tunnel login
```

This will:
1. Open your browser to Cloudflare dashboard
2. Ask you to log in to your Cloudflare account
3. Authorize the tunnel access

## Usage

### Start Tunnel
```bash
./start_tunnel.sh
```

### Check Status
```bash
./check_tunnel.sh
```

### Stop Tunnel
```bash
# Find the process and kill it
pkill -f "cloudflared tunnel"
```

## Troubleshooting

### "Nothing running on port 3000"
- Make sure your React app is started: `cd frontend && npm start`
- Check if something is running: `lsof -i :3000`

### "Waiting for login"
- Complete the authentication in your browser
- Or restart the tunnel after authentication

### "Tunnel not accessible"
- Check that your React app is running
- Verify the tunnel URL is correct
- Try restarting both the app and tunnel

## Security Notes

- This creates a **temporary tunnel** - it will stop when you close the terminal
- The URL is public - anyone with the link can access your app
- Perfect for development, testing, and demos
- For production, consider using a named tunnel with proper authentication

## Next Steps

1. Start your React app: `cd frontend && npm start`
2. Start the tunnel: `./start_tunnel.sh`
3. Copy the provided URL and share it with others
4. Your app is now accessible from anywhere!

## Files Created

- `start_tunnel.sh` - Script to start the tunnel
- `check_tunnel.sh` - Script to check tunnel status
- `CLOUDFLARE_TUNNEL_SETUP.md` - This documentation
