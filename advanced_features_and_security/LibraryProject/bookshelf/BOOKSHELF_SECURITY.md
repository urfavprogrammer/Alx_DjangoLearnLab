# Bookshelf App - CSRF, Security & Data Access Guide

## Overview

This document describes how the bookshelf app implements security best practices for:
1. CSRF (Cross-Site Request Forgery) Protection
2. SQL Injection Prevention
3. Input Validation & Sanitization
4. Content Security Policy (CSP)

---

## 1. CSRF Protection Implementation

### What is CSRF?

Cross-Site Request Forgery (CSRF) is an attack where a malicious website tricks an authenticated user into making unintended requests to your site.

**Example Attack**:
```
1. User logs into bank.com
2. User visits malicious.com (still authenticated to bank.com)
3. malicious.com submits a form: <form action="bank.com/transfer" method="POST">
4. Bank transfers user's money (user didn't intend this!)
```

### CSRF Protection in Bookshelf

#### 1.1 Middleware Protection
Django's `CsrfViewMiddleware` (enabled in settings.py) protects against CSRF by:
- Generating unique CSRF tokens for each user session
- Validating CSRF tokens on POST/PUT/PATCH/DELETE requests
- Rejecting requests with invalid or missing tokens (returns 403 Forbidden)

#### 1.2 Template Implementation

**All form templates include the CSRF token**:
```html
<form method="post">
    {% csrf_token %}
    <input type="text" name="title" />
    <button type="submit">Submit</button>
</form>
```

**Files with CSRF tokens**:
- `bookshelf/templates/bookshelf/book_form.html`
- `bookshelf/templates/bookshelf/book_list.html` (search form)
- `bookshelf/templates/bookshelf/book_confirm_delete.html`

#### 1.3 Settings Configuration

In `LibraryProject/settings.py`:
```python
# CSRF token security
CSRF_COOKIE_SECURE = True       # Send only over HTTPS
CSRF_COOKIE_HTTPONLY = True     # No JavaScript access
CSRF_TRUSTED_ORIGINS = [...]    # Allowed origins
```

#### 1.4 Testing CSRF Protection

**Test 1: Verify CSRF token is required**
```bash
# Try submitting form WITHOUT CSRF token
curl -X POST http://localhost:8000/bookshelf/add/ \
  -d "title=Test&author=Test&publication_year=2023"

# Expected: 403 Forbidden (CSRF token missing)
```

**Test 2: Verify GET requests don't need CSRF**
```bash
# GET requests don't modify data, so they don't need CSRF tokens
curl http://localhost:8000/bookshelf/books/

# Expected: 200 OK (no CSRF needed)
```

---

## 2. SQL Injection Prevention

### What is SQL Injection?

SQL Injection is an attack where user input is interpreted as SQL code, allowing attackers to read/modify/delete database data.

**Example Attack**:
```python
# VULNERABLE CODE:
search_query = request.GET.get('q')
books = Book.objects.raw(f"SELECT * FROM books WHERE title = '{search_query}'")

# Attack input: ' OR '1'='1
# Results in: SELECT * FROM books WHERE title = '' OR '1'='1'
# Returns ALL books (authentication bypass)
```

### SQL Injection Prevention in Bookshelf

#### 2.1 Safe ORM Queries

**SAFE** (Parameterized via Django ORM):
```python
# In bookshelf/views.py - book_list view
search_query = search_form.cleaned_data.get('search_query', '').strip()
if search_query:
    # Django ORM automatically parameterizes the query
    books = books.filter(
        Q(title__icontains=search_query) |
        Q(author__icontains=search_query)
    )
```

**How it works**:
- Django sends: `SELECT * FROM books WHERE title LIKE ? OR author LIKE ?`
- Django sends parameters: `['%search%', '%search%']` separately
- Database executes with parameters, preventing injection

**UNSAFE** (String formatting - AVOID):
```python
# DON'T DO THIS:
books = Book.objects.raw(f"SELECT * FROM books WHERE title = '{search_query}'")

# DON'T DO THIS:
books = Book.objects.filter(title=f"WHERE title LIKE '{search_query}'")

# DON'T DO THIS:
sql = f"SELECT * FROM books WHERE author = '{author}'"
books = Book.objects.raw(sql)
```

#### 2.2 Safe Lookups by ID

```python
# SAFE: get_object_or_404 uses parameterized queries
book = get_object_or_404(Book, pk=pk)

# SAFE: pk parameter is always treated as a number
Book.objects.filter(pk=user_id)

# SAFE: Django forms validate field types before queries
form = BookForm(request.POST)
if form.is_valid():
    form.save()  # ORM handles the query safely
```

#### 2.3 Input Validation with Forms

In `bookshelf/forms.py`:
```python
class BookSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=200,  # Prevent excessively long inputs
        required=False,
        # Additional validation in clean_search_query method
    )

    def clean_search_query(self):
        """Sanitize search query"""
        query = self.cleaned_data.get('search_query', '').strip()
        # Remove leading/trailing whitespace
        # Optional: reject SQL keywords
        return query
```

#### 2.4 Testing SQL Injection Protection

**Test: Try SQL Injection in search**
```bash
# Search with SQL injection attempt
curl -X POST http://localhost:8000/bookshelf/books/ \
  -d "search_query=' OR '1'='1"

# Expected: Safe search that finds no books (injection prevented)
# NOT: Returns all books (which would indicate vulnerability)
```

---

## 3. Input Validation & Sanitization

### Validation in Forms

In `bookshelf/forms.py`, the `BookForm` includes field-level validation:

```python
class BookForm(forms.ModelForm):
    # Field constraints
    class Meta:
        fields = ['title', 'author', 'publication_year']
    
    def clean_title(self):
        """Custom validation for title"""
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) == 0:
            raise forms.ValidationError('Title cannot be empty.')
        return title.strip()
    
    def clean_publication_year(self):
        """Custom validation for year"""
        year = self.cleaned_data.get('publication_year')
        if year and (year < 1000 or year > 9999):
            raise forms.ValidationError('Year must be between 1000 and 9999.')
        return year
```

### XSS (Cross-Site Scripting) Prevention

**What is XSS?**
An attacker injects malicious scripts into your site, which execute in users' browsers.

**Example Attack**:
```html
<!-- User enters in book title field: -->
<img src=x onerror="alert('XSS')">

<!-- If not escaped, this renders as: -->
<div>{{ book.title }}</div>  <!-- onerror executes! -->
```

**Prevention in Bookshelf**:

1. **Auto-escaping in Templates** (DEFAULT):
```html
<!-- Django auto-escapes by default -->
{{ book.title }}  <!-- <img src=x> becomes &lt;img src=x&gt; -->
```

2. **Never use |safe on user input**:
```html
<!-- SAFE (Django escapes) -->
{{ user_input }}

<!-- UNSAFE (disables escaping) -->
{{ user_input|safe }}  <!-- Only for trusted content! -->
```

3. **Form Validation**:
```python
# forms.py validators ensure clean input
title = forms.CharField(max_length=200)  # Length limit
```

---

## 4. Content Security Policy (CSP)

### What is CSP?

Content Security Policy (CSP) is an HTTP header that restricts which domains can load scripts, styles, images, etc. This prevents XSS attacks.

**Example CSP Header**:
```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' https://cdn.example.com;
```

**What this means**:
- Scripts can only load from this domain (`'self'`)
- Styles can load from this domain or https://cdn.example.com
- Inline scripts are NOT allowed (prevents `<script>alert('xss')</script>`)

### CSP in Bookshelf

#### 4.1 Settings Configuration

In `LibraryProject/settings.py`:
```python
CSP_DEFAULT_SRC = ("'self'",)                           # Default: only this domain
CSP_SCRIPT_SRC = ("'self'",)                            # Scripts: only this domain
CSP_STYLE_SRC = ("'self'",)                             # Styles: only this domain
CSP_IMG_SRC = ("'self'", 'data:', 'https:')            # Images: from domain, data URIs, HTTPS
CSP_FRAME_ANCESTORS = ("'none'",)                       # This site cannot be framed
```

#### 4.2 Implementation Options

**Option A: Django CSP Middleware** (Recommended)
```bash
# Install django-csp
pip install django-csp
```

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'csp.middleware.CSPMiddleware',  # Add this
]

# CSP settings as above
```

**Option B: Manual Headers** (Advanced)
```python
from django.http import HttpResponse

def book_list(request):
    response = render(request, 'book_list.html')
    response['Content-Security-Policy'] = "default-src 'self'"
    return response
```

#### 4.3 Testing CSP

**Check CSP headers**:
```bash
curl -I http://localhost:8000/bookshelf/books/

# Look for header:
# Content-Security-Policy: default-src 'self'; script-src 'self'; ...
```

**Test inline script blocking** (with CSP enabled):
```html
<!-- In a template: -->
<script>alert('This should be blocked by CSP')</script>

<!-- With CSP enabled, browser console shows:
Refused to execute inline script. Content Security Policy does not allow 'unsafe-inline'
-->
```

---

## 5. Security Best Practices Checklist

- [ ] All POST/PUT/DELETE forms include `{% csrf_token %}`
- [ ] CSRF_COOKIE_SECURE and CSRF_COOKIE_HTTPONLY are True
- [ ] All queries use Django ORM (not raw SQL)
- [ ] get_object_or_404() used for lookups
- [ ] Form validation enforced before database operations
- [ ] User input is NOT used in string formatting for queries
- [ ] Template auto-escaping is enabled (default)
- [ ] |safe filter only used on trusted content
- [ ] SECURE_BROWSER_XSS_FILTER enabled
- [ ] X-Frame-Options set to DENY
- [ ] DEBUG = False in production
- [ ] CSP headers configured
- [ ] HTTPS/TLS enabled in production
- [ ] Session/CSRF cookies sent over HTTPS only

---

## 6. Common Mistakes to Avoid

### ❌ DON'T: String formatting in queries
```python
# VULNERABLE:
book = Book.objects.filter(title=f"{user_input}")
Book.objects.raw(f"SELECT * FROM books WHERE id = {pk}")
```

### ✅ DO: Use ORM with parameters
```python
# SAFE:
book = Book.objects.filter(title=user_input)
book = Book.objects.filter(pk=pk)
```

---

### ❌ DON'T: Skip form validation
```python
# VULNERABLE:
title = request.POST.get('title')
author = request.POST.get('author')
Book.objects.create(title=title, author=author)
```

### ✅ DO: Validate with forms
```python
# SAFE:
form = BookForm(request.POST)
if form.is_valid():
    form.save()
```

---

### ❌ DON'T: Use |safe on user input
```html
<!-- VULNERABLE: -->
{{ book.title|safe }}
```

### ✅ DO: Auto-escape by default
```html
<!-- SAFE: -->
{{ book.title }}
```

---

### ❌ DON'T: Skip CSRF tokens
```html
<!-- VULNERABLE: -->
<form method="post">
    <input type="text" name="title" />
</form>
```

### ✅ DO: Include CSRF token
```html
<!-- SAFE: -->
<form method="post">
    {% csrf_token %}
    <input type="text" name="title" />
</form>
```

---

## 7. Further Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/4.2/topics/security/)
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP SQL Injection](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [django-csp Documentation](https://django-csp.readthedocs.io/)

---

**Last Updated**: November 2025  
**Status**: Production Ready
