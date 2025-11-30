from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django.db import IntegrityError

from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


"""
API view configuration and extension hooks for the `api` app.

This module provides class-based DRF views for working with `Book` objects.
Configuration highlights and extension points:

- Parsers: `CreateView` and `UpdateView` specify `parser_classes` to accept
    `JSONParser`, `FormParser`, and `MultiPartParser`, so endpoints accept JSON
    bodies as well as form-encoded and file uploads.

- Permissions: `ListView` and `DetailView` are open for read-only access
    (`permissions.AllowAny`). `CreateView`, `UpdateView`, and `DeleteView` are
    restricted to authenticated users (`permissions.IsAuthenticated`) by
    default. There's also an example `IsStaffOrReadOnly` permission class in
    this file you can swap in to restrict unsafe methods to staff users.

- Filtering Hook: `ListView.get_queryset()` demonstrates a small filter
    hook supporting `?author=`, `?year=` and `?title=` query params. Extend or
    replace this with DjangoFilterBackend or custom filters for more features.

- Validation & DB Error Handling: `CreateView.create()` and
    `UpdateView.update()` override DRF defaults to wrap database
    `IntegrityError`s and return clear 400 responses. DRF's
    `ValidationError` handling is preserved for serializer validation errors.

Replace or extend any of the above behaviors as needed for your app.
"""


# Custom permission class: read-only for everyone, write access for staff users.
class IsStaffOrReadOnly(permissions.BasePermission):
    """Allow safe methods for any request, require staff for unsafe methods."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class ListView(generics.ListAPIView):
    """List all books with optional filtering support.

    Filtering supported via query params:
    - `?author=<id>` to filter by author id
    - `?year=<int>` to filter by `publication_year`
    - `?title=<str>` to perform a case-insensitive contains search on title
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        author_id = self.request.query_params.get('author')
        year = self.request.query_params.get('year')
        title = self.request.query_params.get('title')
        if author_id:
            qs = qs.filter(author_id=author_id)
        if year:
            try:
                qs = qs.filter(publication_year=int(year))
            except ValueError:
                pass
        if title:
            qs = qs.filter(title__icontains=title)
        return qs


class DetailView(generics.RetrieveAPIView):
    """Retrieve a specific book by its ID."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


class CreateView(generics.CreateAPIView):
    """Create a new book.

    Customizations:
    - Accept form data and multipart uploads in addition to JSON.
    - Require authentication to create (`IsAuthenticatedOrReadOnly` behavior).
    - Provide clear handling of serializer validation and DB integrity errors.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except IntegrityError as exc:
            return Response({'detail': 'Database integrity error', 'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        # Let DRF handle ValidationError exceptions (they return 400 automatically)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UpdateView(generics.UpdateAPIView):
    """Update an existing book.

    Customizations:
    - Accept form and JSON inputs.
    - Only staff users may perform updates (use `IsStaffOrReadOnly`).
    - Provide explicit validation and DB error handling.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    # Restrict updates to authenticated users only (read-only for unauthenticated)
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except IntegrityError as exc:
            return Response({'detail': 'Database integrity error', 'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)


class DeleteView(generics.DestroyAPIView):
    """Delete a specific book (authenticated users only)."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # Only authenticated users may delete. If you want more granular
    # control (e.g. staff-only or owner-only), replace this with a custom
    # permission class.
    permission_classes = [permissions.IsAuthenticated]
