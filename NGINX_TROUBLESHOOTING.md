# Nginx Deployment Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. **A La Carte Menu Not Loading on Server**

**Problem**: Works on localhost but not on nginx server

**Solutions**:

#### A. Check API Proxy Configuration
```bash
# Test if API is accessible
curl -I http://your-domain.com/api/health
curl -I http://your-domain.com/api/services
```

#### B. Check nginx error logs
```bash
sudo tail -f /var/log/nginx/error.log
```

#### C. Verify CORS headers in nginx config
Make sure your nginx config includes:
```nginx
location /api/ {
    proxy_pass http://localhost:8000;
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
}
```

### 2. **Date/Time Not Loading on Server**

**Problem**: Date formatting works locally but fails on server

**Solutions**:

#### A. Check JavaScript console errors
Open browser dev tools and check for:
- Network errors (404, 500, CORS)
- JavaScript errors
- Console warnings

#### B. Verify static file serving
```bash
# Check if static files are served correctly
curl -I http://your-domain.com/static/js/main.js
curl -I http://your-domain.com/static/css/main.css
```

#### C. Check nginx static file configuration
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Access-Control-Allow-Origin *;
    try_files $uri =404;
}
```

### 3. **React Router Not Working**

**Problem**: Direct URLs return 404

**Solution**: Add this to your nginx config:
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### 4. **Backend Connection Issues**

**Problem**: API calls fail with connection errors

**Solutions**:

#### A. Check if backend is running
```bash
sudo netstat -tlnp | grep :8000
# or
sudo ss -tlnp | grep :8000
```

#### B. Test backend directly
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/services
```

#### C. Check firewall
```bash
sudo ufw status
sudo ufw allow 8000
```

### 5. **CORS Issues**

**Problem**: Browser blocks API requests due to CORS

**Solutions**:

#### A. Add CORS headers to nginx
```nginx
location /api/ {
    proxy_pass http://localhost:8000;
    
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
```

### 6. **Environment Variables Not Working**

**Problem**: Environment variables work locally but not on server

**Solutions**:

#### A. Check if .env file exists in build
```bash
ls -la /var/www/maidsofcyfair/.env
```

#### B. Build with production environment
```bash
NODE_ENV=production npm run build
```

#### C. Set environment variables in nginx
```nginx
location / {
    try_files $uri $uri/ /index.html;
    
    # Set environment variables
    add_header X-Environment "production";
}
```

## 🔧 Quick Fix Commands

### 1. **Restart Services**
```bash
# Restart nginx
sudo systemctl restart nginx

# Restart backend (if using systemd)
sudo systemctl restart your-backend-service

# Check status
sudo systemctl status nginx
sudo systemctl status your-backend-service
```

### 2. **Test Configuration**
```bash
# Test nginx config
sudo nginx -t

# Test API endpoints
curl -I http://localhost:8000/health
curl -I http://your-domain.com/api/health

# Test static files
curl -I http://your-domain.com/static/js/main.js
```

### 3. **Check Logs**
```bash
# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Backend logs (if using systemd)
sudo journalctl -u your-backend-service -f
```

### 4. **Verify File Permissions**
```bash
# Check nginx user
ps aux | grep nginx

# Set correct permissions
sudo chown -R www-data:www-data /var/www/maidsofcyfair
sudo chmod -R 755 /var/www/maidsofcyfair
```

## 🚀 Complete Deployment Checklist

1. **✅ Backend is running on port 8000**
2. **✅ React app is built successfully**
3. **✅ Static files are copied to nginx directory**
4. **✅ Nginx configuration includes API proxy**
5. **✅ CORS headers are properly set**
6. **✅ React Router fallback is configured**
7. **✅ Static file caching is configured**
8. **✅ File permissions are correct**
9. **✅ Nginx configuration is tested**
10. **✅ Services are restarted**

## 📞 Still Having Issues?

If you're still experiencing problems:

1. **Check browser console** for JavaScript errors
2. **Check network tab** for failed requests
3. **Verify all URLs** are accessible
4. **Test API endpoints** directly
5. **Check nginx and backend logs**

## 🔍 Debug Commands

```bash
# Check what's listening on port 80
sudo netstat -tlnp | grep :80

# Check nginx processes
ps aux | grep nginx

# Test nginx configuration
sudo nginx -t

# Check file permissions
ls -la /var/www/maidsofcyfair/

# Test API connectivity
curl -v http://localhost:8000/api/services

# Test static file serving
curl -I http://your-domain.com/static/js/main.js
```
