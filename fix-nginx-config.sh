#!/bin/bash

# Fix nginx configuration for React app deployment
# This script fixes the issue where all requests are proxied to backend

echo "🔧 Fixing nginx configuration for React app..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script with sudo"
    echo "Usage: sudo ./fix-nginx-config.sh"
    exit 1
fi

# Backup current configuration
echo "📦 Backing up current nginx configuration..."
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)

# Create the correct nginx configuration
echo "⚙️ Creating correct nginx configuration..."
cat > /etc/nginx/sites-available/maidsofcyfair << 'EOF'
# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name foodsensescale.tech www.foodsensescale.tech;
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name foodsensescale.tech www.foodsensescale.tech;

    ssl_certificate /etc/letsencrypt/live/foodsensescale.tech/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/foodsensescale.tech/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Root directory for your React app build files
    root /var/www/maidsofcyfair;
    index index.html;

    # Gzip compression for better performance
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
        
        # CORS headers for API requests
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

    # Handle health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Handle static assets with proper caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin *;
        try_files $uri =404;
    }

    # Handle React Router - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Error pages
    error_page 404 /index.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF

# Enable the new site
echo "🔗 Enabling new nginx site..."
ln -sf /etc/nginx/sites-available/maidsofcyfair /etc/nginx/sites-enabled/

# Disable default site
if [ -L /etc/nginx/sites-enabled/default ]; then
    echo "🚫 Disabling default nginx site..."
    rm /etc/nginx/sites-enabled/default
fi

# Create React app directory if it doesn't exist
echo "📁 Creating React app directory..."
mkdir -p /var/www/maidsofcyfair

# Set proper permissions
echo "🔐 Setting permissions..."
chown -R www-data:www-data /var/www/maidsofcyfair
chmod -R 755 /var/www/maidsofcyfair

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid"
    
    # Reload nginx
    echo "🔄 Reloading nginx..."
    systemctl reload nginx
    
    echo "✅ Nginx configuration updated successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Build your React app: cd frontend && npm run build"
    echo "2. Copy build files to nginx: sudo cp -r frontend/build/* /var/www/maidsofcyfair/"
    echo "3. Set permissions: sudo chown -R www-data:www-data /var/www/maidsofcyfair"
    echo "4. Test your application: https://foodsensescale.tech"
    echo ""
    echo "🔍 To check if everything is working:"
    echo "   curl -I https://foodsensescale.tech"
    echo "   curl -I https://foodsensescale.tech/api/health"
    echo "   curl -I https://foodsensescale.tech/static/js/main.js"
else
    echo "❌ Nginx configuration has errors. Please check the configuration file."
    echo "Configuration file: /etc/nginx/sites-available/maidsofcyfair"
    echo "Run: nginx -t"
fi

echo ""
echo "🔍 To check nginx status: systemctl status nginx"
echo "📝 To view nginx logs: tail -f /var/log/nginx/error.log"
echo "🌐 To test your site: curl -I https://foodsensescale.tech"
