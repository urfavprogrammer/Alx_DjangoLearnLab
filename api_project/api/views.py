"""API views for the `api` app.

Authentication and permissions summary
-------------------------------------
- This project enables DRF Token Authentication (see `settings.py`). Clients
	authenticate by supplying the header `Authorization: Token <token>`.
- `BookList` requires authenticated access (either token or session auth).
- `BookViewSet` is restricted to admin users (uses `IsAdminUser`) which
	prevents regular authenticated users from creating/updating/deleting books.

How to obtain a token
---------------------
- POST credentials to the endpoint `/api/api-token-auth/` with fields
	`username` and `password`. The endpoint returns a JSON object with the
	user's token: `{ "token": "<key>" }`.
- You can also create a token in the Django shell:
	`from rest_framework.authtoken.models import Token; Token.objects.get_or_create(user=user)`

Example curl usage
------------------
- Obtain token:
	`curl -X POST -d "username=testuser&password=testpass" http://127.0.0.1:8000/api/api-token-auth/`
- Access protected list with token:
	`curl -H "Authorization: Token <token>" http://127.0.0.1:8000/api/books/`
"""

from rest_framework import generics, viewsets, permissions
from .models import Book
from .serializers import BookSerializer


class BookList(generics.ListAPIView):
		"""List all books; requires authenticated requests.

		Permission: `IsAuthenticated` — anonymous requests will receive 401.
		Authentication: `TokenAuthentication` or `SessionAuthentication`.
		"""
		queryset = Book.objects.all()
		serializer_class = BookSerializer
		permission_classes = [permissions.IsAuthenticated]


class BookViewSet(viewsets.ModelViewSet):
		"""CRUD viewset for books restricted to admin users.

		Permission: `IsAdminUser` — only users with `is_staff`/admin privileges
		can create/update/delete (and list via the router endpoint).
		"""
		queryset = Book.objects.all()
		serializer_class = BookSerializer
		permission_classes = [permissions.IsAdminUser]