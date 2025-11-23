"""URL routes for the `api` app.

This module exposes:
- `books/` -> `BookList` (requires authentication)
- `api-token-auth/` -> DRF's token obtain endpoint. POST `username` & `password`
    to receive a token in response: `{ "token": "<key>" }`.
- router endpoints (registered `BookViewSet` at `books_all/`) — admin-only.

Examples:
 - Obtain token: `curl -X POST -d "username=testuser&password=testpass" http://127.0.0.1:8000/api/api-token-auth/`
 - Use token: `curl -H "Authorization: Token <token>" http://127.0.0.1:8000/api/books/`
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import BookList, BookViewSet


router = DefaultRouter()
router.register(r'books_all', BookViewSet, basename='book_all')

urlpatterns = [
        path('books/', BookList.as_view(), name='book-list'),
        path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
        path('', include(router.urls)),
]
