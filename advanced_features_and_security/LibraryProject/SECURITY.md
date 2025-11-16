# Security Implementation Guide

## Overview

This document details the security measures implemented in the LibraryProject Django application to protect against common web vulnerabilities including XSS, CSRF, SQL injection, and other attacks.

---

## 1. Secure Settings Configuration

### File: `LibraryProject/settings.py`

#### 1.1 Debug Mode
```python
DEBUG = False  # Set to False in production
```
**Why**: When DEBUG=True, Django exposes sensitive information in error pages (SQL queries, settings, installed apps, etc.). Always disable in production.

#### 1.2 Allowed Hosts
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'yourdomain.com']
```
**Why**: Prevents Host header injection attacks. Configure with your actual domain in production.

---

## 2. CSRF Protection

### 2.1 Settings Configuration
```python
CSRF_COOKIE_SECURE = True       # Send CSRF cookie over HTTPS only
CSRF_COOKIE_HTTPONLY = True     # Prevent JavaScript from accessing CSRF cookie
CSRF_TRUSTED_ORIGINS = [...]    # Add trusted origins for CSRF
```

### 2.2 Middleware
Django's `CsrfViewMiddleware` is enabled by default in settings.py. It:
- Validates CSRF tokens on all POST/PUT/DELETE requests
- Automatically generates CSRF tokens for forms
- Rejects requests with invalid or missing tokens

### 2.3 Template Implementation
All form templates include the CSRF token:
```html
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>
```

**Files with CSRF tokens**:
- `relationship_app/templates/login.html`
- `relationship_app/templates/register.html`
- `relationship_app/templates/book_form.html`
- `relationship_app/templates/book_confirm_delete.html`

---

## 3. SQL Injection Prevention

### 3.1 Django ORM Usage
All database queries use Django's ORM with parameterized queries:

**Safe** (Parameterized):
```python
# In relationship_app/views.py
books = Book.objects.select_related('author').all()
book = Book.objects.filter(libraries__pk=library_pk)  # pk is parameterized
```

**Unsafe** (Avoided):
```python
# Never do this:
books = Book.objects.raw("SELECT * FROM books WHERE title = '" + user_input + "'")
# Or this:
Book.objects.filter(title=f"SELECT * FROM {user_input}")
```

### 3.2 View Security Comments
Each view in `relationship_app/views.py` includes comments explaining why it's secure:
- `list_books()`: Uses ORM without user input
- `LibraryBooksView`: Uses `filter()` with parameterized queries
- `add_book()`, `edit_book()`, `delete_book()`: Use `get_object_or_404()` and form validation

---

## 4. XSS (Cross-Site Scripting) Prevention

### 4.1 Settings
```python
SECURE_BROWSER_XSS_FILTER = True      # Enable X-XSS-Protection header
SECURE_CONTENT_TYPE_NOSNIFF = True    # Prevent MIME type sniffing (X-Content-Type-Options)
```

### 4.2 Template Auto-Escaping
Django automatically escapes all template variables:
```django
{{ book.title }}  {# Auto-escaped: < becomes &lt; #}
```

### 4.3 Safe Content
To render HTML (use only for trusted content):
```django
{{ content|safe }}  {# Mark as safe only for trusted sources #}
```

---

## 5. Clickjacking Prevention

### 5.1 Settings
```python
X_FRAME_OPTIONS = 'DENY'  # Prevent embedding in iframes
```

### 5.2 Middleware
`XFrameOptionsMiddleware` is enabled, which:
- Sets `X-Frame-Options: DENY` header
- Prevents this application from being framed by other sites
- Protects against clickjacking attacks

---

## 6. HTTPS / Transport Layer Security

### 6.1 Settings
```python
SECURE_SSL_REDIRECT = True              # Redirect HTTP to HTTPS
SECURE_HSTS_SECONDS = 31536000         # Enforce HTTPS for 1 year (Strict-Transport-Security)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Apply HSTS to subdomains
SESSION_COOKIE_SECURE = True           # Send session cookie over HTTPS only
```

**Deployment Note**: These settings require a valid HTTPS certificate. Use Let's Encrypt for free certificates in production.

---

## 7. Password Security

### 7.1 Settings
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Preferred
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Fallback
]
```

**Why Argon2?**
- Memory-hard algorithm resistant to GPU/ASIC attacks
- Slower than simpler algorithms, making brute-force harder
- Industry best practice (recommended by OWASP)

### 7.2 Password Validation
```python
AUTH_PASSWORD_VALIDATORS = [
    'UserAttributeSimilarityValidator',      # Prevents passwords like username
    'MinimumLengthValidator',                # Minimum 8 characters
    'CommonPasswordValidator',               # Rejects common passwords
    'NumericPasswordValidator',              # Prevents all-numeric passwords
]
```

---

## 8. Content Security Policy (CSP)

### 8.1 Settings
```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", 'data:', 'https:')
CSP_FRAME_ANCESTORS = ("'none'",)
```

**What CSP Does**:
- Restricts where content (scripts, styles, images) can be loaded from
- Prevents inline script execution (mitigation for XSS)
- Requires Django's CSP middleware for enforcement

**Note**: To use CSP, install and enable `django-csp`:
```bash
pip install django-csp
```
Then add `'csp.middleware.CSPMiddleware'` to MIDDLEWARE in settings.py.

---

## 9. Permission-Based Access Control

### 9.1 Custom Permissions
Book model defines custom permissions:
```python
class Meta:
    permissions = (
        ('can_view', 'Can view book (custom)'),
        ('can_create', 'Can create book (custom)'),
        ('can_edit', 'Can edit book (custom)'),
        ('can_delete', 'Can delete book (custom)'),
    )
```

### 9.2 View Protection
All sensitive views use `@permission_required()` decorator:
```python
@permission_required('bookshelf.can_create', raise_exception=True)
def add_book(request):
    ...
```

**Behavior**:
- `raise_exception=True`: Returns 403 Forbidden if user lacks permission
- Without `raise_exception=True`: Redirects to login page
- Enforces group-based access control

### 9.3 Groups and Permissions
Three groups are configured via `create_groups` management command:

**Admins**: All permissions (view, create, edit, delete)
**Editors**: Create, edit, and view permissions
**Viewers**: View only

---

## 10. Input Validation and Sanitization

### 10.1 Django Forms
All user input is validated through Django forms:
```python
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']
```

**Validations**:
- Field type validation (CharField, IntegerField)
- Required field checks
- Length constraints
- Custom validators (if defined)

### 10.2 View Validation
```python
if form.is_valid():
    form.save()  # Only save if all validations pass
```

---

## 11. Authentication and Session Security

### 11.1 Settings
```python
SESSION_COOKIE_SECURE = True     # Send session over HTTPS only
SESSION_COOKIE_HTTPONLY = True   # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # Prevent CSRF via cookies
```

### 11.2 User Registration
Uses Django's `UserCreationForm`:
- Validates password strength
- Automatically hashes passwords (never stored in plain text)
- Implements password confirmation

---

## 12. Security Checklist for Deployment

- [ ] Set `DEBUG = False` in production
- [ ] Update `SECRET_KEY` to a strong, random value (load from environment)
- [ ] Configure `ALLOWED_HOSTS` with your actual domain
- [ ] Set up HTTPS/TLS with a valid certificate
- [ ] Enable `SECURE_SSL_REDIRECT = True`
- [ ] Use a production database (PostgreSQL, MySQL) instead of SQLite
- [ ] Set up a production web server (gunicorn, uWSGI)
- [ ] Configure logging for security events
- [ ] Enable monitoring and alerting
- [ ] Regularly update Django and dependencies
- [ ] Perform security audits and penetration testing
- [ ] Back up sensitive data and test recovery procedures
- [ ] Use environment variables for secrets (SECRET_KEY, API keys, DB credentials)

---

## 13. Testing Security

### 13.1 Manual Testing
1. **CSRF**: Try submitting a form without CSRF token (should fail)
2. **Permissions**: Log in as different users (admin, editor, viewer) and test access
3. **SQL Injection**: Attempt to inject SQL in search fields (should fail gracefully)
4. **XSS**: Try submitting `<script>alert('xss')</script>` in form fields (should be escaped)

### 13.2 Security Headers
Check response headers using browser DevTools or `curl`:
```bash
curl -I https://yourdomain.com
```

Expected headers:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

### 13.3 Automated Testing
Run Django security checks:
```bash
python manage.py check --deploy
```

---

## 14. Useful Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/4.2/topics/security/)
- [OWASP Top 10](https://owasp.org/Top10/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [django-csp](https://django-csp.readthedocs.io/)

---

## 15. Contact and Support

For security issues or vulnerabilities discovered, please follow responsible disclosure:
1. Do NOT publicly disclose the vulnerability
2. Contact the project maintainers privately
3. Allow reasonable time for a fix before public disclosure

---

**Last Updated**: November 2025
**Django Version**: 4.2.25
**Status**: Production Ready (with deployment setup)
