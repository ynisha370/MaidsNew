#!/bin/bash

# React App Deployment Script for Nginx
# This script builds and deploys your React app to nginx

echo "🚀 Deploying React app to nginx..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Please run this script from the frontend directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the React app
echo "🔨 Building React app..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "❌ Build failed. Please check for errors."
    exit 1
fi

echo "✅ Build completed successfully!"

# Create deployment directory
DEPLOY_DIR="/var/www/maidsofcyfair"
echo "📁 Creating deployment directory: $DEPLOY_DIR"
sudo mkdir -p $DEPLOY_DIR

# Copy build files
echo "📋 Copying build files..."
sudo cp -r build/* $DEPLOY_DIR/

# Set proper permissions
echo "🔐 Setting permissions..."
sudo chown -R www-data:www-data $DEPLOY_DIR
sudo chmod -R 755 $DEPLOY_DIR

# Create nginx configuration
echo "⚙️ Creating nginx configuration..."
sudo tee /etc/nginx/sites-available/maidsofcyfair > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    
    root /var/www/maidsofcyfair;
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
    
    # Handle API requests
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

# Enable the site
echo "🔗 Enabling nginx site..."
sudo ln -sf /etc/nginx/sites-available/maidsofcyfair /etc/nginx/sites-enabled/

# Disable default site
if [ -L /etc/nginx/sites-enabled/default ]; then
    echo "🚫 Disabling default site..."
    sudo rm /etc/nginx/sites-enabled/default
fi

# Test and reload nginx
echo "🧪 Testing nginx configuration..."
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
    echo "🔄 Reloading nginx..."
    sudo systemctl reload nginx
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "🌐 Your app should now be accessible at:"
    echo "   http://your-server-ip"
    echo ""
    echo "🔍 To check if everything is working:"
    echo "   curl -I http://your-server-ip"
    echo "   curl -I http://your-server-ip/api/health"
else
    echo "❌ Nginx configuration has errors"
    echo "Please check: sudo nginx -t"
fi
