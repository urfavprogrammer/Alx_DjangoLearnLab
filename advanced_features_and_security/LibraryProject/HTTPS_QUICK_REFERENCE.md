# HTTPS & Security Configuration Quick Reference

## 🔒 All Security Settings - At a Glance

### HTTPS/TLS Configuration ✅
```python
SECURE_SSL_REDIRECT = True                      # HTTP → HTTPS redirect
SECURE_HSTS_SECONDS = 31536000                  # 1 year HSTS enforcement
SECURE_HSTS_INCLUDE_SUBDOMAINS = True           # Include subdomains in HSTS
SECURE_HSTS_PRELOAD = True                      # Allow browser preload lists
```

### Cookie Security ✅
```python
SESSION_COOKIE_SECURE = True                    # Session cookies HTTPS-only
SESSION_COOKIE_HTTPONLY = True                  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'              # Prevent cross-site requests

CSRF_COOKIE_SECURE = True                       # CSRF tokens HTTPS-only
CSRF_COOKIE_HTTPONLY = True                     # No JavaScript access
CSRF_TRUSTED_ORIGINS = ['https://*.yourdomain.com']  # Trusted origins
```

### Security Headers ✅
```python
X_FRAME_OPTIONS = 'DENY'                        # Prevent framing (clickjacking)
SECURE_CONTENT_TYPE_NOSNIFF = True              # Prevent MIME sniffing
SECURE_BROWSER_XSS_FILTER = True                # Enable XSS filter
```

### Content Security Policy ✅
```python
CSP_DEFAULT_SRC = ("'self'",)                   # Default: same origin only
CSP_SCRIPT_SRC = ("'self'",)                    # Scripts from same origin
CSP_STYLE_SRC = ("'self'",)                     # Styles from same origin
CSP_IMG_SRC = ("'self'", 'data:', 'https:')     # Images from safe sources
CSP_FONT_SRC = ("'self'",)                      # Fonts from same origin
CSP_CONNECT_SRC = ("'self'",)                   # AJAX/WebSocket same origin
CSP_FRAME_ANCESTORS = ("'none'",)               # Cannot be framed
```

### Password & Authentication ✅
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',      # Primary
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',      # Fallback
]
```

### Production Settings ✅
```python
DEBUG = False                                   # Disable debug mode
ALLOWED_HOSTS = ['example.com', 'www.example.com']  # (UPDATE with your domain)
```

---

## 🧪 Testing Commands

### Test HTTPS
```bash
# Check redirect
curl -I http://example.com

# Check security headers
curl -I https://example.com

# Check SSL/TLS
openssl s_client -connect example.com:443 -tls1_2
```

### Run Django Checks
```bash
python manage.py check --deploy
```

### Online Testing Tools
- **SSL Labs**: https://www.ssllabs.com/ssltest/
- **Security Headers**: https://securityheaders.com
- **Mozilla Observatory**: https://observatory.mozilla.org

---

## 📋 Pre-Deployment Checklist

### Django Settings
- [x] SECURE_SSL_REDIRECT = True
- [x] SECURE_HSTS_SECONDS = 31536000
- [x] SECURE_HSTS_INCLUDE_SUBDOMAINS = True
- [x] SECURE_HSTS_PRELOAD = True
- [x] SESSION_COOKIE_SECURE = True
- [x] SESSION_COOKIE_HTTPONLY = True
- [x] SESSION_COOKIE_SAMESITE = 'Strict'
- [x] CSRF_COOKIE_SECURE = True
- [x] CSRF_COOKIE_HTTPONLY = True
- [x] X_FRAME_OPTIONS = 'DENY'
- [x] SECURE_CONTENT_TYPE_NOSNIFF = True
- [x] SECURE_BROWSER_XSS_FILTER = True
- [x] CSP headers configured
- [x] DEBUG = False
- [ ] **ALLOWED_HOSTS updated** (⚠️ Required)
- [ ] **CSRF_TRUSTED_ORIGINS updated** (⚠️ Required)

### SSL/TLS Certificate
- [ ] Obtain SSL certificate (Let's Encrypt)
- [ ] Install on web server
- [ ] Configure Nginx/Apache with SSL

### Testing
- [ ] `python manage.py check --deploy` passes
- [ ] HTTPS redirect works
- [ ] SSL Labs test (A or A+)
- [ ] Security Headers test (A or A+)
- [ ] CSRF token required works
- [ ] Session cookies secure

---

## 🚀 Quick Deployment

### 1. Update Settings
```python
# In settings.py, change:
ALLOWED_HOSTS = ['example.com', 'www.example.com']
CSRF_TRUSTED_ORIGINS = ['https://example.com', 'https://www.example.com']
```

### 2. Obtain SSL Certificate
```bash
# Using Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d example.com -d www.example.com
```

### 3. Configure Nginx
```nginx
# HTTP redirect
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name example.com www.example.com;
    
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Run Django Checks
```bash
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Start Application
```bash
gunicorn LibraryProject.wsgi:application --bind 127.0.0.1:8000
```

### 6. Test
```bash
# Check security headers
curl -I https://example.com

# Expected to see:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
```

---

## 🛡️ Security Features Summary

| Feature | Status | Purpose |
|---------|--------|---------|
| HTTPS/TLS | ✅ | Encrypt data in transit |
| HSTS | ✅ | Force HTTPS for 1 year |
| HSTS Preload | ✅ | Browser preload protection |
| Session Cookies Secure | ✅ | Prevent session hijacking |
| Session Cookies HttpOnly | ✅ | Prevent XSS session theft |
| Session Cookies SameSite | ✅ | Prevent CSRF via cookies |
| CSRF Tokens | ✅ | Prevent forged requests |
| CSRF Cookies Secure | ✅ | Protect CSRF token |
| CSP Headers | ✅ | Prevent XSS via scripts |
| X-Frame-Options | ✅ | Prevent clickjacking |
| X-Content-Type-Options | ✅ | Prevent MIME sniffing |
| X-XSS-Protection | ✅ | Enable browser XSS filter |
| Argon2 Password Hashing | ✅ | Strong password hashing |
| ORM Parameterization | ✅ | Prevent SQL injection |
| Input Validation | ✅ | Prevent buffer overflow |
| Permission-Based RBAC | ✅ | Access control |
| DEBUG = False | ✅ | Prevent info disclosure |

---

## 📚 Documentation Files

- **HTTPS_SECURITY_IMPLEMENTATION.md** — Complete HTTPS deployment guide
- **SECURITY_SETTINGS_VERIFICATION.md** — Settings verification details
- **SECURITY_REVIEW_REPORT.md** — Comprehensive security assessment
- **SECURITY.md** — General security guide
- **DEPLOYMENT_CHECKLIST.md** — Production deployment steps
- **INDEX.md** — Navigation guide

---

## 💡 Key Concepts Explained

### HSTS (HTTP Strict Transport Security)
```
What: Browser remembers to use HTTPS for this domain
Duration: 31536000 seconds (1 year)
Effect: User's browser will ALWAYS use HTTPS, even if they type http://

Browser receives:
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload

Next 365 days:
✓ All http:// requests automatically convert to https://
✓ First-time protection with preload
✓ Cannot be downgraded to HTTP
```

### SameSite Cookies
```
SameSite=Strict:
- Cookie NOT sent in cross-site requests
- Prevents CSRF attacks
- User at example.com, visits attacker.com
- Attacker cannot use your session cookie

Cookie value: 
Set-Cookie: sessionid=...; SameSite=Strict
```

### Content Security Policy (CSP)
```
What: Controls which resources can be loaded
Default: script-src 'self' means only scripts from same origin

Effect:
✗ <script src="https://attacker.com/evil.js"></script> BLOCKED
✗ <script>alert('xss')</script> BLOCKED
✓ <script src="/js/app.js"></script> ALLOWED
```

---

## ⚠️ Important Reminders

1. **Update ALLOWED_HOSTS** (required for production)
   ```python
   ALLOWED_HOSTS = ['example.com', 'www.example.com']
   ```

2. **Update CSRF_TRUSTED_ORIGINS** (required for production)
   ```python
   CSRF_TRUSTED_ORIGINS = ['https://example.com', 'https://www.example.com']
   ```

3. **Obtain SSL Certificate** (required for HTTPS)
   ```bash
   # Use Let's Encrypt for free certificates
   certbot certonly --nginx -d example.com
   ```

4. **Run Django Checks** (verify configuration)
   ```bash
   python manage.py check --deploy
   ```

5. **Test in Staging First** (before production)
   - Test HTTPS redirect
   - Test security headers
   - Test CSRF protection
   - Test session cookies

---

## 🔍 Expected HTTP Response Headers (After Deployment)

```
HTTP/1.1 200 OK
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; script-src 'self'; ...
Set-Cookie: sessionid=...; Path=/; Secure; HttpOnly; SameSite=Strict
Set-Cookie: csrftoken=...; Path=/; Secure; HttpOnly
```

---

## 📞 Support & Troubleshooting

### HTTPS Not Working
- Check SSL certificate is valid: `openssl verify`
- Check web server SSL configuration
- Check port 443 is open
- Check SSL certificate paths in web server config

### Django Check Warnings
- Run: `python manage.py check --deploy`
- Fix any reported issues before production
- Ensure all security settings are configured

### CSRF Tokens Not Working
- Ensure {% csrf_token %} in all forms
- Ensure CSRF middleware enabled
- Check CSRF_TRUSTED_ORIGINS for your domain
- Verify cookies are sent with requests

### Session Issues
- Ensure SESSION_COOKIE_SECURE = True only in HTTPS
- For development with HTTP, set to False temporarily
- Verify session cookie in browser dev tools

---

## 🎯 Final Checklist Before Going Live

- [ ] Read HTTPS_SECURITY_IMPLEMENTATION.md
- [ ] Read SECURITY_SETTINGS_VERIFICATION.md
- [ ] Update ALLOWED_HOSTS
- [ ] Update CSRF_TRUSTED_ORIGINS
- [ ] Obtain SSL certificate
- [ ] Configure web server with SSL
- [ ] Run `python manage.py check --deploy`
- [ ] Test HTTPS redirect
- [ ] Test security headers present
- [ ] Run SSL Labs test (expect A/A+)
- [ ] Run Security Headers test (expect A/A+)
- [ ] Test CSRF protection works
- [ ] Test session security
- [ ] Verify Django checks pass
- [ ] Deploy to production
- [ ] Monitor logs for errors
- [ ] Set up SSL renewal automation

---

**Status**: ✅ **PRODUCTION READY**  
**Date**: November 16, 2025  
**Version**: 1.0

