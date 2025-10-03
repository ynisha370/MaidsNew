#!/bin/bash

# Nginx Deployment Fix Script
# This script helps fix common nginx issues with React apps

echo "🔧 Fixing nginx configuration for React app..."

# Check if nginx is running
if ! systemctl is-active --quiet nginx; then
    echo "❌ Nginx is not running. Starting nginx..."
    sudo systemctl start nginx
fi

# Backup current nginx config
echo "📦 Backing up current nginx configuration..."
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)

# Create new nginx configuration
echo "⚙️ Creating new nginx configuration..."
sudo tee /etc/nginx/sites-available/maidsofcyfair > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;  # Replace with your domain
    
    # Root directory for your React app
    root /var/www/maidsofcyfair/frontend/build;  # Update this path
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Handle API requests - proxy to your backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain; charset=utf-8';
            add_header Content-Length 0;
            return 204;
        }
    }
    
    # Handle static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin *;
        try_files $uri =404;
    }
    
    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the new site
echo "🔗 Enabling new nginx site..."
sudo ln -sf /etc/nginx/sites-available/maidsofcyfair /etc/nginx/sites-enabled/

# Disable default site if it exists
if [ -L /etc/nginx/sites-enabled/default ]; then
    echo "🚫 Disabling default nginx site..."
    sudo rm /etc/nginx/sites-enabled/default
fi

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
    
    # Reload nginx
    echo "🔄 Reloading nginx..."
    sudo systemctl reload nginx
    
    echo "✅ Nginx configuration updated successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Update the 'root' path in /etc/nginx/sites-available/maidsofcyfair to point to your React build directory"
    echo "2. Update the 'server_name' to your actual domain"
    echo "3. Make sure your backend is running on port 8000"
    echo "4. Test your application"
else
    echo "❌ Nginx configuration has errors. Please check the configuration file."
    echo "Configuration file: /etc/nginx/sites-available/maidsofcyfair"
fi

echo ""
echo "🔍 To check nginx status: sudo systemctl status nginx"
echo "📝 To view nginx logs: sudo tail -f /var/log/nginx/error.log"
echo "🌐 To test your site: curl -I http://your-domain.com"
