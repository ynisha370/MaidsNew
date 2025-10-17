# Maids of CyFair - PM2 & Nginx Setup

This document provides instructions for running the Maids of CyFair application using PM2 process manager and Nginx reverse proxy.

## 🚀 Quick Start

### Start All Services
```bash
cd /root/MaidsNew
./start_services.sh
```

### Stop All Services
```bash
cd /root/MaidsNew
./stop_services.sh
```

### Restart All Services
```bash
cd /root/MaidsNew
./restart_services.sh
```

## 📋 Prerequisites

- Node.js (v20+)
- Python 3.13+
- PM2 (installed globally)
- Nginx
- MongoDB (running locally or remotely)

## 🏗️ Architecture

```
Internet → Nginx (Port 80) → Frontend (Port 3000) / Backend API (Port 8000)
```

- **Frontend**: React application served on port 3000
- **Backend**: FastAPI application served on port 8000
- **Nginx**: Reverse proxy on port 80, routes requests to appropriate services
- **PM2**: Process manager for both frontend and backend

## 📁 Configuration Files

### PM2 Configuration (`ecosystem.config.js`)
- Manages both frontend and backend processes
- Auto-restart on failure
- Log management
- Memory limits and monitoring

### Nginx Configuration (`nginx.conf`)
- Reverse proxy setup
- CORS headers for API
- Static file caching
- Security headers
- Gzip compression

### Environment Files
- `backend/.env`: Backend environment variables
- `frontend/.env`: Frontend environment variables

## 🔧 Service Management

### PM2 Commands
```bash
# View status
pm2 status

# View logs
pm2 logs

# View specific service logs
pm2 logs maids-backend
pm2 logs maids-frontend

# Restart specific service
pm2 restart maids-backend
pm2 restart maids-frontend

# Stop specific service
pm2 stop maids-backend
pm2 stop maids-frontend

# Delete specific service
pm2 delete maids-backend
pm2 delete maids-frontend

# Monitor resources
pm2 monit
```

### Nginx Commands
```bash
# Test configuration
nginx -t

# Reload configuration
systemctl reload nginx

# Restart Nginx
systemctl restart nginx

# Check status
systemctl status nginx

# View logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 🌐 Access Points

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api
- **API Documentation**: http://localhost/api/docs

## 📊 Monitoring

### Application Logs
```bash
# PM2 logs
pm2 logs

# Application-specific logs
tail -f /root/MaidsNew/logs/backend.log
tail -f /root/MaidsNew/logs/frontend.log
tail -f /root/MaidsNew/logs/backend-error.log
tail -f /root/MaidsNew/logs/frontend-error.log
```

### System Logs
```bash
# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System logs
journalctl -u nginx
journalctl -u pm2-root
```

## 🔄 Auto-Start on Boot

PM2 is configured to start automatically on system boot:
```bash
# Check if PM2 startup is configured
pm2 startup

# Save current process list
pm2 save
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :80
   lsof -i :3000
   lsof -i :8000
   
   # Kill the process
   kill -9 <PID>
   ```

2. **PM2 Process Not Starting**
   ```bash
   # Check PM2 logs
   pm2 logs
   
   # Check application logs
   tail -f /root/MaidsNew/logs/*.log
   ```

3. **Nginx Configuration Error**
   ```bash
   # Test configuration
   nginx -t
   
   # Check Nginx error logs
   tail -f /var/log/nginx/error.log
   ```

4. **Permission Issues**
   ```bash
   # Make scripts executable
   chmod +x /root/MaidsNew/*.sh
   
   # Check file permissions
   ls -la /root/MaidsNew/
   ```

### Health Checks

```bash
# Check if services are responding
curl -I http://localhost
curl -I http://localhost/api/

# Check PM2 status
pm2 status

# Check Nginx status
systemctl status nginx
```

## 🔧 Customization

### Environment Variables

Edit the environment files to customize your setup:

**Backend (`backend/.env`)**:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=maidsofcyfair
JWT_SECRET=your_secret_key
# ... other variables
```

**Frontend (`frontend/.env`)**:
```env
REACT_APP_BACKEND_URL=http://localhost
REACT_APP_STRIPE_PUBLISHABLE_KEY=your_stripe_key
# ... other variables
```

### Nginx Configuration

Edit `/root/MaidsNew/nginx.conf` to customize:
- Server name
- SSL certificates
- Caching rules
- Security headers

### PM2 Configuration

Edit `/root/MaidsNew/ecosystem.config.js` to customize:
- Process instances
- Memory limits
- Restart policies
- Environment variables

## 📈 Performance Optimization

### PM2 Clustering
To enable clustering for better performance, modify `ecosystem.config.js`:
```javascript
{
  name: 'maids-backend',
  script: 'venv/bin/python',
  args: 'server.py',
  instances: 'max', // Use all CPU cores
  exec_mode: 'cluster'
}
```

### Nginx Optimization
- Enable gzip compression (already configured)
- Set appropriate cache headers
- Configure worker processes based on CPU cores

## 🔒 Security Considerations

- Change default JWT secrets
- Configure proper CORS policies
- Set up SSL/TLS certificates
- Regular security updates
- Monitor logs for suspicious activity

## 📞 Support

For issues or questions:
1. Check the logs first
2. Verify configuration files
3. Test individual components
4. Check system resources (CPU, memory, disk)

## 🎯 Next Steps

1. Configure your domain name
2. Set up SSL certificates
3. Configure production environment variables
4. Set up monitoring and alerting
5. Configure backup strategies

