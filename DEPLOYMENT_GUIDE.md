# 🚀 Complete Deployment Guide for React App on Nginx

## 🚨 **Your Current Problem**

Your nginx configuration is **proxying ALL requests** to the backend (port 8000), but your React app needs to be served as **static files**. This is why:
- ✅ A la carte menu works on localhost (served by React dev server)
- ❌ A la carte menu doesn't work on server (all requests go to backend)

## 🔧 **The Fix**

You need to change your nginx configuration to:
1. **Serve React static files** for the main app
2. **Proxy only API requests** (`/api/*`) to the backend
3. **Handle React Router** properly

## 📋 **Step-by-Step Solution**

### **Step 1: Update Nginx Configuration**

Replace your current nginx configuration with this:

```nginx
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

    # 🎯 KEY CHANGE: Root directory for React app
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

    # 🎯 KEY CHANGE: Only proxy API requests to backend
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

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static assets with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin *;
        try_files $uri =404;
    }

    # 🎯 KEY CHANGE: Serve React app for all other requests
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
```

### **Step 2: Build and Deploy React App**

```bash
# 1. Build your React app
cd frontend
npm run build

# 2. Create nginx directory
sudo mkdir -p /var/www/maidsofcyfair

# 3. Copy build files to nginx
sudo cp -r build/* /var/www/maidsofcyfair/

# 4. Set proper permissions
sudo chown -R www-data:www-data /var/www/maidsofcyfair
sudo chmod -R 755 /var/www/maidsofcyfair
```

### **Step 3: Update Nginx Configuration**

```bash
# 1. Backup current config
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# 2. Create new config file
sudo nano /etc/nginx/sites-available/maidsofcyfair
# Paste the configuration above

# 3. Enable the new site
sudo ln -sf /etc/nginx/sites-available/maidsofcyfair /etc/nginx/sites-enabled/

# 4. Disable default site
sudo rm /etc/nginx/sites-enabled/default

# 5. Test configuration
sudo nginx -t

# 6. Reload nginx
sudo systemctl reload nginx
```

### **Step 4: Test Everything**

```bash
# Test React app
curl -I https://foodsensescale.tech

# Test API endpoints
curl -I https://foodsensescale.tech/api/health
curl -I https://foodsensescale.tech/api/services

# Test static files
curl -I https://foodsensescale.tech/static/js/main.js
curl -I https://foodsensescale.tech/static/css/main.css
```

## 🔍 **What This Fixes**

### **Before (Your Current Config):**
```
All requests → Backend (port 8000)
├── / → Backend (❌ Should serve React)
├── /api/services → Backend (✅ Correct)
├── /static/js/main.js → Backend (❌ Should serve static file)
└── /login → Backend (❌ Should serve React)
```

### **After (Fixed Config):**
```
├── / → React app (✅ Correct)
├── /api/services → Backend (✅ Correct)
├── /static/js/main.js → Static file (✅ Correct)
└── /login → React app (✅ Correct)
```

## 🚨 **Common Issues & Solutions**

### **Issue 1: 404 for React routes**
**Solution**: Make sure you have `try_files $uri $uri/ /index.html;` in the `/` location block

### **Issue 2: API requests fail**
**Solution**: Check that your backend is running on port 8000 and accessible

### **Issue 3: Static files not loading**
**Solution**: Verify the `root` directive points to your React build directory

### **Issue 4: CORS errors**
**Solution**: The configuration includes proper CORS headers for API requests

## 📞 **Quick Commands**

```bash
# Check nginx status
sudo systemctl status nginx

# Check nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Check if backend is running
sudo netstat -tlnp | grep :8000
```

## ✅ **Verification Checklist**

- [ ] React app loads at https://foodsensescale.tech
- [ ] API calls work (check browser network tab)
- [ ] A la carte menu loads
- [ ] Date/time displays correctly
- [ ] Static files load (JS, CSS, images)
- [ ] React Router works (direct URLs don't 404)

## 🎯 **Expected Result**

After applying this fix:
- ✅ **React app serves from nginx** (not proxied to backend)
- ✅ **API requests go to backend** (port 8000)
- ✅ **A la carte menu loads** (served by React)
- ✅ **Date/time works** (served by React)
- ✅ **All static files load** (served by nginx)

Your app should now work exactly like it does on localhost! 🎉
