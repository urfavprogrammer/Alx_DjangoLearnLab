# SECURE_PROXY_SSL_HEADER Configuration Guide

## Overview

The `SECURE_PROXY_SSL_HEADER` setting has been added to `LibraryProject/settings.py` to properly handle HTTPS requests when running Django behind a reverse proxy (Nginx, Apache, etc.).

**Setting Added**:
```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

**Location**: `LibraryProject/settings.py` line ~88

---

## Why This Setting Is Important

### The Problem

When you deploy Django behind a reverse proxy (Nginx, Apache):

```
┌─────────────────┐
│   User Browser  │
│   (HTTPS)       │
└────────┬────────┘
         │ HTTPS Connection
         ▼
┌──────────────────┐
│  Nginx Proxy     │
│ (Handles HTTPS)  │
└────────┬─────────┘
         │ HTTP Connection (internal)
         ▼
┌──────────────────┐
│  Django App      │
│  (internal port) │
└──────────────────┘
```

**Issue**: Django sees an HTTP request (from Nginx) and doesn't know the original request was HTTPS.

**Consequence Without This Setting**:
- Django thinks the request is insecure
- SECURE_SSL_REDIRECT won't work properly
- SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE cookies won't be set
- Security is compromised

### The Solution

The reverse proxy (Nginx) adds a header to indicate the original protocol:

```
X-Forwarded-Proto: https
```

**With SECURE_PROXY_SSL_HEADER configured**, Django:
1. Looks for the `X-Forwarded-Proto` header
2. Sees the value is `https`
3. Treats the request as secure
4. Sets secure cookies properly
5. All security features work correctly

---

## Current Configuration

### Setting
```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Components Explained

**Tuple Format**: `(header_name, expected_value)`

**1. Header Name: `'HTTP_X_FORWARDED_PROTO'`**
- The HTTP header to look for
- Format: `'HTTP_' + header_name_with_underscores`
- Standard header: `X-Forwarded-Proto`
- Django translates: `X-Forwarded-Proto` → `HTTP_X_FORWARDED_PROTO`

**2. Expected Value: `'https'`**
- The value that indicates a secure connection
- When Nginx sends: `X-Forwarded-Proto: https`
- Django recognizes it and treats request as secure

### How It Works

```python
# Django's Process
Request comes in from Nginx with headers:
    X-Forwarded-Proto: https
    X-Real-IP: 203.0.113.5
    X-Forwarded-For: 203.0.113.5

Django checks SECURE_PROXY_SSL_HEADER:
    Is 'HTTP_X_FORWARDED_PROTO' header present? YES
    Is its value 'https'? YES
    → Request is treated as SECURE

Result:
✅ SECURE_SSL_REDIRECT works
✅ SESSION_COOKIE_SECURE cookies are set
✅ CSRF_COOKIE_SECURE cookies are set
✅ Security headers respect HTTPS
```

---

## Nginx Configuration Required

For this setting to work, your Nginx configuration must add the header:

### Nginx Configuration Example

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        
        # CRITICAL: Add this header so Django knows request was HTTPS
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Other important headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
    }
}
```

**Key Line**:
```nginx
proxy_set_header X-Forwarded-Proto $scheme;
```

This tells Nginx to:
- Add header `X-Forwarded-Proto`
- Set it to the request scheme (`http` or `https`)
- Pass it to Django

---

## Security Implications

### ✅ With SECURE_PROXY_SSL_HEADER Configured

When Nginx adds the header correctly:

```nginx
proxy_set_header X-Forwarded-Proto $scheme;
```

Django receives:
```
X-Forwarded-Proto: https
```

Result:
- ✅ SECURE_SSL_REDIRECT enforced
- ✅ SESSION_COOKIE_SECURE = True (cookies sent only via HTTPS)
- ✅ CSRF_COOKIE_SECURE = True (CSRF tokens sent only via HTTPS)
- ✅ Cookies properly encrypted in transit
- ✅ All security features work correctly

**Security Status**: ✅ **SECURE**

---

### ❌ Without SECURE_PROXY_SSL_HEADER (If Not Configured)

Django receives:
```
X-Forwarded-Proto: https (but setting is not configured)
```

Django doesn't check the header:
- ❌ SECURE_SSL_REDIRECT not enforced
- ❌ SESSION_COOKIE_SECURE not applied
- ❌ CSRF_COOKIE_SECURE not applied
- ❌ Cookies sent over insecure connection
- ❌ Session can be intercepted
- ❌ CSRF protection compromised

**Security Status**: ❌ **INSECURE**

---

### ⚠️ Without Nginx Header (If Nginx Not Configured)

Even with Django setting configured, if Nginx doesn't send the header:

Django receives:
```
(No X-Forwarded-Proto header)
```

Django can't verify the request is HTTPS:
- ❌ SECURE_SSL_REDIRECT not enforced
- ❌ Secure cookies not set
- ❌ All security features fail

**Security Status**: ❌ **INSECURE**

**Fix**: Update Nginx to add:
```nginx
proxy_set_header X-Forwarded-Proto $scheme;
```

---

## Deployment Checklist

### Before Production

- [x] Django setting configured: `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`
- [ ] **Nginx configured to add header**: `proxy_set_header X-Forwarded-Proto $scheme;`
- [ ] Test that header is being sent (see testing section below)
- [ ] Verify secure cookies are set
- [ ] Test HTTPS redirect works

### Verification

Test that everything is working:

```bash
# 1. Check Nginx is adding the header
curl -v https://example.com/

# Look for in response headers:
# Set-Cookie: sessionid=...; Secure; HttpOnly
#                            ^^^^^^
#             Only set if X-Forwarded-Proto: https received

# 2. Check Django logs for HTTPS request
# Should show: "GET / HTTP/1.1" with secure=True

# 3. Test CSRF protection works
# Try POST without CSRF token
curl -X POST https://example.com/bookshelf/add/
# Expected: 403 Forbidden (CSRF protection working)
```

---

## Other Reverse Proxies

### Apache (mod_proxy)

```apache
<Location />
    ProxyPass http://127.0.0.1:8000/
    ProxyPassReverse http://127.0.0.1:8000/
    ProxyPreserveHost On
    
    # Add the header for Django
    RequestHeader set X-Forwarded-Proto "https"
</Location>
```

### Gunicorn Behind Nginx

```python
# gunicorn_config.py
forwarded_allow_ips = "127.0.0.1,::1"  # Allow localhost (Nginx)
```

This allows Gunicorn to trust the X-Forwarded headers from Nginx.

### AWS Load Balancer

AWS ELB adds headers automatically. Configure Django to trust it:

```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Same setting - AWS ELB adds X-Forwarded-Proto header
```

### CloudFront / CDN

```python
# CloudFront adds CF-Visitor header
# But standard X-Forwarded-Proto also works
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

## When NOT to Use This Setting

### ⚠️ Development Environment

**In development** (runserver), you typically don't use a reverse proxy:

```python
# settings_dev.py
SECURE_PROXY_SSL_HEADER = None  # Not needed in development

# Or leave it out entirely - it only applies if header is present
```

### ⚠️ Direct Access to Django

If users access Django directly without a reverse proxy:

```
Browser → Django (direct, no proxy)
```

**Don't add SECURE_PROXY_SSL_HEADER** - there's no proxy to add the header.

---

## Security Risks & Mitigations

### Risk: Trusting Untrusted Headers

If you add `SECURE_PROXY_SSL_HEADER` but the header comes from an untrusted source, an attacker could spoof the header:

```
Attacker's request:
GET / HTTP/1.0
X-Forwarded-Proto: https  ← Attacker spoofs this!
```

**Mitigation**: Only configure `SECURE_PROXY_SSL_HEADER` if:
1. You run behind a reverse proxy you control
2. Direct access to Django from internet is blocked
3. Only the proxy can add headers to requests

**Nginx Configuration (Restrict Access)**:
```nginx
# Only allow Nginx to talk to Django
listen 127.0.0.1:8000;  # Listen only on localhost

# Block direct internet access
# Configure firewall to block port 8000 from internet
```

---

## Testing

### Manual Testing

1. **Check Response Headers**:
```bash
curl -v https://example.com/login/
```

Look for in response:
```
Set-Cookie: sessionid=abc123; Path=/; Secure; HttpOnly; SameSite=Strict
                                           ^^^^^^
                        Should have Secure flag if HTTPS
```

2. **Test CSRF Protection**:
```bash
# Try POST without CSRF token
curl -X POST https://example.com/bookshelf/add/ \
  -d "title=Test&author=Test&publication_year=2023"
# Should return 403 Forbidden
```

3. **Check Nginx Header**:
```bash
# In Nginx logs, check request headers received by Django
# tail -f /var/log/nginx/access.log

# Verify X-Forwarded-Proto is present
proxy_set_header X-Forwarded-Proto $scheme;
```

### Django Testing

```python
# test_secure_headers.py
from django.test import Client
from django.test import TestCase

class SecureHeadersTest(TestCase):
    def test_secure_cookies_set(self):
        client = Client()
        
        # Make request with X-Forwarded-Proto header (simulating Nginx)
        response = client.get(
            '/login/',
            HTTP_X_FORWARDED_PROTO='https'
        )
        
        # Check if Set-Cookie has Secure flag
        self.assertIn('Secure', str(response.cookies['sessionid']))
        self.assertIn('HttpOnly', str(response.cookies['sessionid']))
```

---

## Configuration Reference

### Current Setting in settings.py

```python
# Line 88 of LibraryProject/settings.py
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Common Variations

```python
# Standard (current) - Nginx, Apache, most proxies
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CloudFlare (also accepts above)
SECURE_PROXY_SSL_HEADER = ('HTTP_CF_VISITOR', 'https')  # Optional alternative

# AWS ELB
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Same

# If you don't have a reverse proxy (direct access):
# Don't set it - leave commented or None
SECURE_PROXY_SSL_HEADER = None
```

### Disabling (If Needed)

```python
# To disable this setting:
SECURE_PROXY_SSL_HEADER = None

# Or comment it out:
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

## Nginx Configuration Template

Complete Nginx configuration for production with Django:

```nginx
# /etc/nginx/sites-available/libraryproject

# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    
    return 301 https://$server_name$request_uri;
}

# HTTPS server - main application
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name example.com www.example.com;
    
    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Django Application
    location / {
        # CRITICAL: Tell Django that original request was HTTPS
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Other important headers
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
    }
    
    # Static files (optional optimization)
    location /static/ {
        alias /path/to/LibraryProject/static/;
        expires 30d;
    }
}
```

**Key Line for This Setting**:
```nginx
proxy_set_header X-Forwarded-Proto $scheme;
```

---

## Summary

### What Was Added
```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Why It's Important
- Enables Django to recognize HTTPS requests from reverse proxies
- Required for secure cookies to work with Nginx/Apache
- Critical for production deployments

### What You Need to Do
1. ✅ Django setting is configured
2. [ ] Configure Nginx to add the header:
   ```nginx
   proxy_set_header X-Forwarded-Proto $scheme;
   ```
3. [ ] Test that secure cookies are set
4. [ ] Verify HTTPS redirect works

### Security Requirement
**Both must be configured**:
- ✅ Django: `SECURE_PROXY_SSL_HEADER` (done)
- [ ] Nginx: `proxy_set_header X-Forwarded-Proto $scheme;` (your responsibility)

**If only Django is configured but Nginx doesn't send the header**, security features will not work properly.

---

**Setting Added**: ✅ COMPLETE  
**Status**: Ready for deployment (with proper Nginx configuration)  
**Security Impact**: CRITICAL for production with reverse proxy

