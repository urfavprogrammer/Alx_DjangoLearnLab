"""
Serializers for the API models.

This module defines how `Author` and `Book` instances are converted to/from
primitive Python datatypes for rendering as JSON (and for validation when
creating/updating instances).

Relationship handling summary:
- `AuthorSerializer` exposes an author's `books` as a nested read-only list
    using `BookSerializer(many=True, read_only=True)`. This is convenient for
    endpoints that need to display an author together with their books.
- `BookSerializer` represents the `author` field by primary key (writeable)
    using `PrimaryKeyRelatedField`. That means when creating or updating a book
    you provide the `author` id (pk). If you want a writable nested author
    representation instead, you would replace the PK field with a nested
    `AuthorSerializer` and implement create/update logic to handle nested data.
"""

from datetime import datetime
from rest_framework import serializers
from .models import Book, Author


class BookSerializer(serializers.ModelSerializer):
        """Serializer for `Book` model.

        - Exposes `title`, `publication_year` and `author`.
        - `author` is represented as a writeable primary-key field so clients
            create/update books by providing an `author` id.
        """
        # Explicitly show the author as a writable PK related field. This makes
        # intent clear and provides a QuerySet for validation on writes.
        author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())

        class Meta:
                model = Book
                # Use the DRF convention for including all model fields
                fields = '__all__'

        # Field-level validation hook for `publication_year`.
        # DRF will call `validate_<fieldname>` for the field before full validation.
        def validate_publication_year(self, value):
                current_year = datetime.now().year
                if value > current_year:
                        raise serializers.ValidationError("Publication year cannot be in the future.")
                return value



class AuthorSerializer(serializers.ModelSerializer):
        """Serializer for `Author` model.

        - Exposes the author's `name` and a nested, read-only list of `books`.
        - The `books` field uses `BookSerializer(many=True, read_only=True)` which
            will serialize each related `Book` using `BookSerializer` but will not
            accept book data on author create/update (read-only).
        """
        books = BookSerializer(many=True, read_only=True)

        class Meta:
                model = Author
                fields = ['id', 'name', 'books']

