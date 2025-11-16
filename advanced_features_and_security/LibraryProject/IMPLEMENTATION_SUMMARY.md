# LibraryProject - Complete Security & Access Control Implementation

## Executive Summary

This document summarizes all the security enhancements and access control features implemented in the LibraryProject Django application.

---

## Part 1: Groups and Permissions System

### Custom Permissions Defined

The `Book` model (in `bookshelf/models.py`) defines four custom permissions:

```python
class Meta:
    permissions = (
        ('can_view', 'Can view book (custom)'),
        ('can_create', 'Can create book (custom)'),
        ('can_edit', 'Can edit book (custom)'),
        ('can_delete', 'Can delete book (custom)'),
    )
```

### Groups and Permission Assignment

Three groups are created with specific permission sets:

| Group    | Permissions                | Use Case              |
|----------|---------------------------|----------------------|
| **Admins**   | view, create, edit, delete | Full book management |
| **Editors**  | view, create, edit         | Content creators     |
| **Viewers**  | view                       | Read-only access     |

### Setup Commands

```bash
# Create groups and assign permissions
python manage.py create_groups

# Create test users for testing
python manage.py create_test_users

# Test users created:
# - admin_user / password123 (Admins group)
# - editor_user / password123 (Editors group)
# - viewer_user / password123 (Viewers group)
```

### Access Control in Views

All sensitive views are protected with the `@permission_required()` decorator:

**bookshelf/views.py**:
- `add_book()` — Requires `bookshelf.can_create`
- `edit_book()` — Requires `bookshelf.can_edit`
- `delete_book()` — Requires `bookshelf.can_delete`

**relationship_app/views.py**:
- Same views with equivalent permission checks

**Behavior**: Unauthorized users receive a 403 Forbidden response (when `raise_exception=True`).

---

## Part 2: Security Hardening

### Settings Configuration (`LibraryProject/settings.py`)

#### 1. Debug and Hosts
```python
DEBUG = False                               # Disable in production
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'yourdomain.com']
```

#### 2. CSRF Protection
```python
CSRF_COOKIE_SECURE = True          # HTTPS only
CSRF_COOKIE_HTTPONLY = True        # No JavaScript access
CSRF_TRUSTED_ORIGINS = [...]       # Allowed origins
```

#### 3. Session Security
```python
SESSION_COOKIE_SECURE = True       # HTTPS only
SESSION_COOKIE_HTTPONLY = True     # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict' # Prevent cross-site access
```

#### 4. Browser Security Headers
```python
SECURE_BROWSER_XSS_FILTER = True       # X-XSS-Protection
SECURE_CONTENT_TYPE_NOSNIFF = True     # X-Content-Type-Options
X_FRAME_OPTIONS = 'DENY'               # X-Frame-Options
```

#### 5. HTTPS / HSTS
```python
SECURE_SSL_REDIRECT = True             # HTTP → HTTPS
SECURE_HSTS_SECONDS = 31536000         # 1-year HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Include subdomains
SECURE_HSTS_PRELOAD = True             # HSTS preload list
```

#### 6. Password Security
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',   # Primary
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',   # Fallback
]
```

#### 7. Content Security Policy (CSP)
```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", 'data:', 'https:')
CSP_FRAME_ANCESTORS = ("'none'",)
```

### Template Security

All forms include CSRF tokens:
```html
<form method="post">
    {% csrf_token %}
    ...
</form>
```

**Files updated**:
- `login.html`
- `register.html`
- `book_form.html`
- `book_confirm_delete.html`

### View Security

All views use:
1. **Parameterized ORM queries** — prevents SQL injection
2. **`get_object_or_404()`** — prevents information disclosure
3. **Form validation** — sanitizes user input
4. **`@permission_required()` decorator** — enforces access control

**Example (edit_book)**:
```python
@permission_required('bookshelf.can_edit', raise_exception=True)
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)  # Safe lookup
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():                # Validates input
            form.save()                    # Safe save
```

---

## Part 3: Documentation

### SECURITY.md
Comprehensive guide covering:
- Secure settings configuration
- CSRF, XSS, clickjacking, and SQL injection prevention
- Password and authentication security
- CSP implementation
- Deployment checklist
- Security testing procedures
- Useful resources

**File**: `LibraryProject/SECURITY.md`

### DEPLOYMENT_CHECKLIST.md
Step-by-step deployment guide including:
- Environment setup
- Database configuration
- Static file collection
- Web server setup (Gunicorn + Nginx)
- HTTPS/TLS configuration
- Logging and monitoring
- Backup procedures
- Post-deployment verification

**File**: `LibraryProject/DEPLOYMENT_CHECKLIST.md`

---

## Part 4: Management Commands

### create_groups
Creates three groups (Admins, Editors, Viewers) and assigns permissions automatically.

```bash
python manage.py create_groups
```

**Output**:
```
Created group: Admins
Created group: Editors
Created group: Viewers
Groups and permissions setup complete.
```

### create_test_users
Creates test users for manual testing:
- `admin_user` (Admins group)
- `editor_user` (Editors group)
- `viewer_user` (Viewers group)

```bash
python manage.py create_test_users
```

---

## Testing Checklist

### Manual Testing

#### 1. Permission Testing
```bash
# Login as admin_user / password123
# → Can add, edit, delete books ✓

# Login as editor_user / password123
# → Can add, edit, but NOT delete books ✓

# Login as viewer_user / password123
# → Can view only (see 403 on add/edit/delete) ✓
```

#### 2. CSRF Testing
```bash
# Try submitting form without {% csrf_token %}
# → Expect 403 Forbidden ✓
```

#### 3. Security Headers
```bash
curl -I https://yourdomain.com
# Expected:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block
# Strict-Transport-Security: max-age=31536000
```

### Automated Testing
```bash
# Check Django security settings
python manage.py check --deploy

# Check for vulnerable dependencies
pip install safety && safety check
```

---

## Security Features Summary

| Feature | Status | Implemented In |
|---------|--------|-----------------|
| DEBUG disabled in production | ✓ | settings.py |
| CSRF protection | ✓ | Middleware + templates |
| SQL injection prevention | ✓ | ORM usage in views |
| XSS protection | ✓ | Auto-escaping + headers |
| Clickjacking prevention | ✓ | X-Frame-Options header |
| HTTPS/HSTS enforcement | ✓ | settings.py (deploy stage) |
| Secure password hashing | ✓ | Argon2PasswordHasher |
| Permission-based access control | ✓ | @permission_required |
| Group-based authorization | ✓ | Groups + permissions |
| Input validation | ✓ | Django forms |
| Session security | ✓ | Secure cookies |
| Security headers | ✓ | settings.py |
| CSP implementation | ✓ | settings.py (optional middleware) |

---

## Deployment Notes

### Development
```bash
# For testing locally, create a .env file:
DEBUG=True
SECRET_KEY=your-dev-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Production
```bash
# Update settings.py or use environment variables:
DEBUG=False
SECRET_KEY=<use environment variable>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Initial Deployment
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Create groups and permissions
python manage.py create_groups

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Create superuser
python manage.py createsuperuser

# 6. Run security checks
python manage.py check --deploy

# 7. Start web server (Gunicorn)
gunicorn LibraryProject.wsgi:application --bind 0.0.0.0:8000
```

---

## File Listing

### Key Files Modified/Created

```
LibraryProject/
├── LibraryProject/
│   ├── settings.py              ← Security settings added
│   └── wsgi.py
├── bookshelf/
│   ├── models.py                ← Custom permissions defined
│   ├── views.py                 ← Protected views with permissions
│   └── management/commands/
│       ├── create_groups.py     ← NEW: Create groups
│       └── create_test_users.py ← NEW: Create test users
├── relationship_app/
│   ├── views.py                 ← Security comments added
│   └── templates/
│       ├── login.html           ← CSRF token present
│       ├── register.html        ← CSRF token present
│       ├── book_form.html       ← CSRF token present
│       └── book_confirm_delete.html ← CSRF token present
├── SECURITY.md                  ← NEW: Security guide
├── DEPLOYMENT_CHECKLIST.md      ← NEW: Deployment guide
└── README.md (this file)
```

---

## Recommended Next Steps

1. **Review SECURITY.md** for detailed security implementation details
2. **Review DEPLOYMENT_CHECKLIST.md** before deploying to production
3. **Run `python manage.py check --deploy`** to verify settings
4. **Test with different user roles** to verify access control
5. **Set up monitoring and logging** as outlined in DEPLOYMENT_CHECKLIST.md
6. **Configure HTTPS/TLS** using Let's Encrypt or your certificate provider
7. **Perform penetration testing** before going live
8. **Set up automated backups** for data recovery

---

## Support and Questions

Refer to:
- `SECURITY.md` — Detailed security explanations
- `DEPLOYMENT_CHECKLIST.md` — Production deployment steps
- [Django Security Documentation](https://docs.djangoproject.com/en/4.2/topics/security/)
- [OWASP Top 10](https://owasp.org/Top10/)

---

**Last Updated**: November 2025  
**Django Version**: 4.2.25  
**Status**: Production Ready (with proper deployment setup)
