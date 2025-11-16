# Deployment Checklist

Use this checklist when deploying the LibraryProject to production.

## Pre-Deployment

### Environment Setup
- [ ] Create a `.env` file with production secrets (do NOT commit to git)
  ```env
  SECRET_KEY=your-secret-key-here
  DEBUG=False
  ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
  DB_ENGINE=django.db.backends.postgresql
  DB_NAME=library_db
  DB_USER=db_user
  DB_PASSWORD=secure_password
  DB_HOST=database.example.com
  DB_PORT=5432
  ```

### Code Deployment
- [ ] Clone/pull latest code from repository
- [ ] Verify all tests pass: `python manage.py test`
- [ ] Run security checks: `python manage.py check --deploy`
- [ ] Check for deprecated settings: `python manage.py check --deploy --fail-level WARNING`

### Dependencies
- [ ] Update requirements.txt: `pip freeze > requirements.txt`
- [ ] Install production dependencies: `pip install -r requirements.txt`
- [ ] Install wsgi server: `pip install gunicorn` or `pip install uWSGI`
- [ ] (Optional) Install CSP middleware: `pip install django-csp`

---

## Database Setup

### PostgreSQL (Recommended for Production)
- [ ] Create database: `createdb library_db`
- [ ] Create database user: `createuser db_user`
- [ ] Grant privileges: `psql -c "ALTER USER db_user WITH PASSWORD 'secure_password';"`

### Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Initial Data
```bash
# Create groups and assign permissions
python manage.py create_groups

# Create test users (optional, for testing only)
python manage.py create_test_users

# Create superuser for admin
python manage.py createsuperuser
```

---

## Static and Media Files

- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Configure web server to serve static files at `/static/`
- [ ] Create media directory and configure permissions
- [ ] Set up S3 or other cloud storage for media files (recommended for scalability)

---

## Web Server Configuration

### Gunicorn Setup
```bash
# Install gunicorn
pip install gunicorn

# Run gunicorn
gunicorn LibraryProject.wsgi:application --bind 0.0.0.0:8000 --workers 4 --worker-class sync
```

### Systemd Service (for auto-startup)
Create `/etc/systemd/system/libraryproject.service`:
```ini
[Unit]
Description=LibraryProject Django App
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/LibraryProject
ExecStart=/path/to/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:/path/to/libraryproject.sock \
    LibraryProject.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable libraryproject
sudo systemctl start libraryproject
```

---

## Nginx Reverse Proxy Configuration

Create `/etc/nginx/sites-available/libraryproject`:
```nginx
upstream libraryproject {
    server unix:/path/to/libraryproject.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS Header
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Client Upload Size
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://libraryproject;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    location /static/ {
        alias /path/to/LibraryProject/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/LibraryProject/media/;
        expires 7d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/libraryproject /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

---

## HTTPS/TLS Setup

### Let's Encrypt (Free)
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo systemctl enable certbot.timer
```

### Settings Update
In `settings.py`:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

---

## Logging and Monitoring

### Django Logging
Update `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/libraryproject/django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### System Monitoring
- [ ] Set up monitoring tool (Prometheus, New Relic, DataDog)
- [ ] Configure alerts for:
  - High error rates
  - Database connectivity issues
  - Memory/CPU usage
  - Disk space

---

## Backup and Disaster Recovery

- [ ] Set up automated database backups (daily minimum)
  ```bash
  # PostgreSQL backup script
  pg_dump -U db_user -h db_host library_db | gzip > backup-$(date +%Y%m%d).sql.gz
  ```
- [ ] Store backups in separate location (S3, external server)
- [ ] Test backup restoration procedure
- [ ] Document disaster recovery procedures

---

## Security Audits

- [ ] Run Django security checks: `python manage.py check --deploy`
- [ ] Check for vulnerable dependencies: `pip install safety && safety check`
- [ ] Review error logs for suspicious activity
- [ ] Perform manual penetration testing or hire professionals
- [ ] Set up Web Application Firewall (WAF) if available

---

## Post-Deployment

- [ ] Verify site is accessible over HTTPS
- [ ] Check security headers are present:
  ```bash
  curl -I https://yourdomain.com
  ```
- [ ] Test user registration and login
- [ ] Verify permission-based access (admin, editor, viewer accounts)
- [ ] Monitor logs for errors
- [ ] Announce availability to users

---

## Ongoing Maintenance

- [ ] Monthly: Review logs and monitoring alerts
- [ ] Monthly: Check for Django security updates
- [ ] Quarterly: Review access logs for suspicious activity
- [ ] Quarterly: Update dependencies to latest secure versions
- [ ] Annually: Perform full security audit
- [ ] As needed: Apply security patches immediately

---

**Last Updated**: November 2025
