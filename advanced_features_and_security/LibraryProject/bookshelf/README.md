# Bookshelf App - Security-First Implementation

## Overview

The bookshelf app demonstrates secure Django development practices including:
- **CSRF Protection** via tokens and middleware
- **SQL Injection Prevention** using Django ORM
- **Input Validation & Sanitization** with forms
- **Permission-Based Access Control** with groups
- **XSS Prevention** via template auto-escaping
- **Content Security Policy** headers

---

## File Structure

```
bookshelf/
├── migrations/           # Database migrations
├── templates/
│   └── bookshelf/
│       ├── book_list.html              # Secure book listing with search
│       ├── book_form.html              # Secure form with CSRF token
│       └── book_confirm_delete.html    # Delete confirmation with CSRF
├── management/
│   └── commands/
│       ├── create_groups.py            # Create groups and assign permissions
│       └── create_test_users.py        # Create test users for testing
├── admin.py                            # Django admin configuration
├── apps.py                             # App configuration
├── forms.py                            # Secure forms with validation
├── models.py                           # Book model with permissions
├── tests.py                            # Unit tests
├── views.py                            # Secure views with decorators
├── urls.py                             # URL routing
├── BOOKSHELF_SECURITY.md               # Detailed security guide
└── README.md                           # This file
```

---

## Security Features

### 1. CSRF Protection ✓

**Templates Include CSRF Token**:
- `book_form.html` — Form for creating/editing books
- `book_list.html` — Search form
- `book_confirm_delete.html` — Delete confirmation form

**Middleware Configuration**:
- `CsrfViewMiddleware` enabled in settings.py
- CSRF token validation on all POST/PUT/DELETE requests
- Returns 403 Forbidden for requests without valid CSRF token

**Settings**:
```python
CSRF_COOKIE_SECURE = True       # HTTPS only
CSRF_COOKIE_HTTPONLY = True     # No JavaScript access
```

### 2. SQL Injection Prevention ✓

**Safe Queries**:
- All database queries use Django ORM
- `get_object_or_404()` for safe lookups
- Parameterized queries prevent SQL injection

**Example** (bookshelf/views.py - book_list):
```python
books = books.filter(
    Q(title__icontains=search_query) |
    Q(author__icontains=search_query)
)
# Django automatically parameterizes this query
```

### 3. Input Validation ✓

**BookForm** (bookshelf/forms.py):
- Validates title and author (non-empty, trimmed)
- Validates publication year (1000-9999)
- Custom clean_* methods for business logic

**BookSearchForm** (bookshelf/forms.py):
- Max length 200 characters
- Sanitizes whitespace
- Prevents buffer overflow attacks

### 4. XSS Prevention ✓

**Template Auto-Escaping**:
```html
{{ book.title }}  <!-- Auto-escaped, safe -->
```

**Never Use |safe on User Input**:
```html
{{ book.title|safe }}  <!-- ONLY for trusted content -->
```

### 5. Permission-Based Access Control ✓

**Decorators**:
```python
@permission_required('bookshelf.can_create', raise_exception=True)
def add_book(request): ...

@permission_required('bookshelf.can_edit', raise_exception=True)
def edit_book(request, pk): ...

@permission_required('bookshelf.can_delete', raise_exception=True)
def delete_book(request, pk): ...
```

**Groups**:
- **Admins** — Full access (view, create, edit, delete)
- **Editors** — Create and edit (view, create, edit)
- **Viewers** — Read-only (view)

---

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Groups and Permissions
```bash
python manage.py create_groups
```

Output:
```
Created group: Admins
Created group: Editors
Created group: Viewers
Groups and permissions setup complete.
```

### 4. Create Test Users (Optional)
```bash
python manage.py create_test_users
```

Users created:
- `admin_user` / `password123` (Admins group — full access)
- `editor_user` / `password123` (Editors group — create/edit)
- `viewer_user` / `password123` (Viewers group — read-only)

---

## Testing Security

### Test 1: CSRF Protection
```bash
# Try submitting a form without CSRF token
curl -X POST http://localhost:8000/bookshelf/add/ \
  -d "title=Test&author=Test&publication_year=2023"

# Expected: 403 Forbidden (CSRF token missing)
```

### Test 2: SQL Injection Prevention
```bash
# Search with SQL injection attempt
curl -X POST http://localhost:8000/bookshelf/books/ \
  -d "search_query=' OR '1'='1"

# Expected: Safe search (no books found, injection prevented)
```

### Test 3: Permission-Based Access
```bash
# Login as viewer_user (limited permissions)
# Try to access add_book page
# Expected: 403 Forbidden (user lacks permission)
```

### Test 4: Input Validation
```bash
# Try to create a book with invalid year
Form submission: publication_year=1234567890

# Expected: Form validation error
```

---

## Key Files to Review

1. **BOOKSHELF_SECURITY.md** — Comprehensive security guide
2. **forms.py** — Form validation and input sanitization
3. **views.py** — Secure view implementation with comments
4. **templates/bookshelf/book_form.html** — Form with CSRF token
5. **templates/bookshelf/book_list.html** — Search with CSRF token
6. **templates/bookshelf/book_confirm_delete.html** — Delete confirmation

---

## Security Best Practices

✅ **DO**:
- Include `{% csrf_token %}` in all form templates
- Use Django ORM for all database queries
- Validate all user input with forms
- Use `get_object_or_404()` for safe lookups
- Check permissions with `@permission_required`
- Auto-escape template variables (default behavior)
- Use HTTPS in production

❌ **DON'T**:
- Use string formatting in SQL queries
- Skip form validation
- Use `|safe` on user input
- Omit CSRF tokens from forms
- Use raw SQL queries with user input
- Disable template auto-escaping
- Store sensitive data in code (use environment variables)

---

## Documentation

- **BOOKSHELF_SECURITY.md** — Detailed security explanations
- **LibraryProject/SECURITY.md** — Project-wide security guide
- **LibraryProject/DEPLOYMENT_CHECKLIST.md** — Production deployment steps
- **LibraryProject/IMPLEMENTATION_SUMMARY.md** — Complete implementation overview

---

## Production Deployment

Before deploying to production:

1. [ ] Run security checks: `python manage.py check --deploy`
2. [ ] Set `DEBUG = False`
3. [ ] Update `ALLOWED_HOSTS`
4. [ ] Enable HTTPS/TLS
5. [ ] Set secure cookie settings
6. [ ] Configure logging and monitoring
7. [ ] Test all security features
8. [ ] Review DEPLOYMENT_CHECKLIST.md

---

## Support and Questions

Refer to:
- `BOOKSHELF_SECURITY.md` — Detailed explanations
- [Django Security Docs](https://docs.djangoproject.com/en/4.2/topics/security/)
- [OWASP Security Guides](https://owasp.org/)

---

**Last Updated**: November 2025  
**Status**: Production Ready  
**Security Level**: High (with proper deployment configuration)
