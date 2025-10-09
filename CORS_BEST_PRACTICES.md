# CORS Best Practices for Cross-Browser Compatibility

## The Golden Rule ⚠️

**NEVER use wildcard origins (`*`) with credentials (`true`)!**

This is the #1 cause of Safari compatibility issues.

---

## ✅ CORRECT CORS Configuration

### When Using Authentication/Cookies

```javascript
// Backend (FastAPI/Python)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "http://localhost:3000"  // for development
    ],
    allow_credentials=True,  // ✅ OK with specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)
```

```nginx
# Nginx
add_header Access-Control-Allow-Origin $http_origin always;
add_header Access-Control-Allow-Credentials "true" always;
```

### When NOT Using Authentication

```javascript
// Public API - no credentials needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  // ✅ OK without credentials
    allow_credentials=False,  // Must be False
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## ❌ INCORRECT CORS Configuration

### Common Mistakes

#### Mistake 1: Wildcard + Credentials
```javascript
// ❌ WRONG - Safari will block ALL requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  // ❌ Wildcard
    allow_credentials=True,  // ❌ With credentials
)
```

**Error in Safari:**
```
Access to fetch at 'https://api.example.com' from origin 'https://example.com' 
has been blocked by CORS policy: The value of the 'Access-Control-Allow-Origin' 
header must not be the wildcard '*' when the request's credentials mode is 'include'.
```

#### Mistake 2: Inconsistent Origins
```javascript
// Frontend
axios.defaults.baseURL = 'https://api.example.com';

// Backend
allow_origins=["https://example.com"]  // ❌ Doesn't match!
```

#### Mistake 3: Missing Credentials in Requests
```javascript
// ❌ WRONG - Safari won't send auth cookies
fetch('https://api.example.com/data', {
    headers: { 'Authorization': 'Bearer token' }
    // Missing: credentials: 'include'
});

// ✅ CORRECT - Safari will send cookies/auth
fetch('https://api.example.com/data', {
    headers: { 'Authorization': 'Bearer token' },
    credentials: 'include'  // ✅ Required for Safari
});
```

---

## Browser Differences

| Browser | Wildcard + Credentials | Missing credentials | Strict Mode |
|---------|------------------------|---------------------|-------------|
| Chrome  | ⚠️ May allow           | ⚠️ May work         | Lenient     |
| Firefox | ⚠️ May allow           | ⚠️ May work         | Lenient     |
| Safari  | ❌ Always blocks       | ❌ Blocks auth      | Strict      |
| Edge    | ⚠️ May allow           | ⚠️ May work         | Lenient     |

**Takeaway:** Always code for Safari's strict standards, and it will work everywhere.

---

## Frontend Configuration

### axios Setup (React/Vue/Angular)

```javascript
// src/index.js or src/main.js
import axios from 'axios';

// Global configuration
axios.defaults.withCredentials = true;
axios.defaults.baseURL = process.env.REACT_APP_BACKEND_URL;
axios.defaults.headers.common['Accept'] = 'application/json';
axios.defaults.headers.common['Content-Type'] = 'application/json';
```

### fetch() Best Practices

```javascript
// Always include credentials for authenticated requests
const response = await fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    credentials: 'include',  // ✅ Always add this
    body: JSON.stringify(data)
});
```

### Environment Variables

```bash
# .env file
REACT_APP_BACKEND_URL=https://yourdomain.com  # No trailing slash
REACT_APP_API_TIMEOUT=10000
```

---

## Backend Configuration

### FastAPI CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "http://localhost:3000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Cache-Control"
    ],
    expose_headers=["Content-Length", "Content-Range", "Authorization"],
    max_age=3600
)
```

### Express.js CORS

```javascript
const cors = require('cors');

app.use(cors({
    origin: [
        'https://yourdomain.com',
        'https://www.yourdomain.com',
        'http://localhost:3000'
    ],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
    allowedHeaders: ['Content-Type', 'Authorization', 'Accept']
}));
```

### Django CORS

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
```

---

## Nginx Configuration

### Basic Setup

```nginx
location /api/ {
    proxy_pass http://localhost:8000;
    
    # Use $http_origin instead of *
    add_header Access-Control-Allow-Origin $http_origin always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH" always;
    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
    add_header Access-Control-Allow-Credentials "true" always;
    add_header Access-Control-Max-Age 1728000 always;
    
    # Handle preflight requests
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin $http_origin always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
        add_header Access-Control-Allow-Credentials "true" always;
        add_header Access-Control-Max-Age 1728000 always;
        add_header Content-Type 'text/plain; charset=utf-8' always;
        add_header Content-Length 0 always;
        return 204;
    }
}
```

### Advanced: Whitelist Specific Origins

```nginx
# Define allowed origins
map $http_origin $cors_origin {
    default "";
    "https://yourdomain.com" $http_origin;
    "https://www.yourdomain.com" $http_origin;
    "http://localhost:3000" $http_origin;
}

location /api/ {
    # Only add CORS headers for whitelisted origins
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Access-Control-Allow-Credentials "true" always;
    # ... rest of config
}
```

---

## Debugging CORS Issues

### 1. Check Headers in Browser DevTools

**Chrome/Firefox/Safari:**
1. Open DevTools (F12)
2. Go to Network tab
3. Click on API request
4. Check Response Headers

**Look for:**
```
Access-Control-Allow-Origin: https://yourdomain.com  ✅
Access-Control-Allow-Credentials: true  ✅
```

**Red flags:**
```
Access-Control-Allow-Origin: *  ❌ (with credentials)
Access-Control-Allow-Credentials: false  ❌
(missing CORS headers entirely)  ❌
```

### 2. Test with curl

```bash
# Test preflight request
curl -X OPTIONS \
  -H "Origin: https://yourdomain.com" \
  -H "Access-Control-Request-Method: POST" \
  -I https://yourdomain.com/api/endpoint

# Should return:
# access-control-allow-origin: https://yourdomain.com
# access-control-allow-credentials: true
```

### 3. Check Console Errors

**Safari-specific error:**
```
CORS policy: The value of the 'Access-Control-Allow-Origin' header 
in the response must not be the wildcard '*' when the request's 
credentials mode is 'include'
```

**Solution:** Use specific origins instead of wildcard.

---

## Security Considerations

### 1. Never Use Wildcard in Production

```javascript
// ❌ INSECURE - allows any site to make authenticated requests
allow_origins=["*"]
allow_credentials=True

// ✅ SECURE - only your domains can make authenticated requests
allow_origins=["https://yourdomain.com"]
allow_credentials=True
```

### 2. Validate Origins Server-Side

```python
# Custom middleware to validate origins
class SecureCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin", "")
        
        allowed_origins = [
            "https://yourdomain.com",
            "https://www.yourdomain.com"
        ]
        
        response = await call_next(request)
        
        # Only add CORS headers for allowed origins
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
```

### 3. Use HTTPS in Production

```bash
# ✅ Always use HTTPS for production
REACT_APP_BACKEND_URL=https://api.yourdomain.com

# ❌ Never use HTTP in production (except localhost)
REACT_APP_BACKEND_URL=http://api.yourdomain.com
```

---

## Testing Checklist

### Before Deploying:

- [ ] Test in Safari (most strict browser)
- [ ] Test in Chrome
- [ ] Test in Firefox
- [ ] Check no CORS errors in console
- [ ] Verify authentication works
- [ ] Test with clear cache
- [ ] Test in incognito/private mode
- [ ] Test on mobile Safari (iOS)
- [ ] Verify credentials are sent
- [ ] Check OPTIONS preflight works

### After Deploying:

- [ ] Clear browser cache
- [ ] Test login functionality
- [ ] Test API calls with authentication
- [ ] Verify cookies are set/sent
- [ ] Check production environment variables
- [ ] Monitor error logs for CORS issues

---

## Quick Reference

| Scenario | Origins | Credentials | Works in Safari? |
|----------|---------|-------------|------------------|
| Public API | `["*"]` | `False` | ✅ Yes |
| Authenticated API | `["specific"]` | `True` | ✅ Yes |
| Authenticated API | `["*"]` | `True` | ❌ **NO** |
| Multiple domains | `["domain1", "domain2"]` | `True` | ✅ Yes |
| Dynamic origin | `$http_origin` (nginx) | `True` | ✅ Yes |

---

## Common Questions

### Q: Can I use regex for origins?
**A:** Not directly in most frameworks. Use a custom middleware to validate against patterns.

### Q: What if I have multiple subdomains?
**A:** List them explicitly or use dynamic origin validation:
```python
allowed_patterns = [r'https://.*\.yourdomain\.com']
```

### Q: Why doesn't `*` work with credentials?
**A:** Security. Wildcard would allow any website to make authenticated requests to your API, which is a major security risk.

### Q: Do I need CORS for same-origin requests?
**A:** No. CORS only applies to cross-origin requests (different domain, port, or protocol).

---

## Resources

- [MDN CORS Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [W3C CORS Specification](https://www.w3.org/TR/cors/)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)
- [Safari Web Inspector Guide](https://developer.apple.com/safari/tools/)

---

**Remember:** If it works in Safari, it works everywhere! 🎯

