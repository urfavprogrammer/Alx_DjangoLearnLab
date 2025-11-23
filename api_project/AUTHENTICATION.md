Authentication & Permissions (DRF Token Auth)
===========================================

Overview
--------
This project uses Django REST Framework with Token Authentication enabled. Tokens
allow clients (scripts, Postman, etc.) to authenticate by sending the header
`Authorization: Token <token>` with requests.

Configuration (where to look)
- `api_project/settings.py` — includes `rest_framework` and `rest_framework.authtoken`
  in `INSTALLED_APPS` and configures `REST_FRAMEWORK` to include
  `TokenAuthentication` in `DEFAULT_AUTHENTICATION_CLASSES`.
- `api/urls.py` — exposes the token retrieval endpoint at
  `/api/api-token-auth/` (DRF's `obtain_auth_token`).
- `api/views.py` — example views show how permission classes are applied:
  - `BookList` uses `IsAuthenticated` (requires a token or session credentials).
  - `BookViewSet` uses `IsAdminUser` (admin-only write operations).

Getting a token
---------------
1. Make sure migrations are applied (this creates the tables used by authtoken):

```bash
python3 manage.py migrate
```

2. Create a user (if you don't have one):

```bash
python3 manage.py createsuperuser
# or via the shell:
python3 manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('testuser','test@example.com','testpass')"
```

3. Obtain the token (POST username & password):

```bash
curl -X POST -d "username=testuser&password=testpass" http://127.0.0.1:8000/api/api-token-auth/
# Response: { "token": "<the-token-key>" }
```

Using the token
---------------
Include the token in the `Authorization` header for protected endpoints:

```bash
curl -H "Authorization: Token <the-token-key>" http://127.0.0.1:8000/api/books/
```

Notes on permissions
--------------------
- `IsAuthenticated` ensures only logged-in users can access the view.
- `IsAdminUser` restricts access to users with admin (staff) privileges.
- The global `DEFAULT_PERMISSION_CLASSES` in settings is `AllowAny` so views
  must explicitly set stricter permissions when required.

If you want me to also add JWT authentication or to enable token creation via
registration endpoints, I can implement that next.
