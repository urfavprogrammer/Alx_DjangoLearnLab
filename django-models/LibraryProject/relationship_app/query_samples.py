"""Sample query functions for the `relationship_app` models.

This script exposes three functions you can call from the Django shell or
run directly (it will configure Django when executed as a script).

Functions:
- books_by_author(author_id) -> QuerySet[Book]
- books_in_library(library_id) -> QuerySet[Book]
- librarian_for_library(library_id) -> Librarian | None

Usage (from project root):
  ./django-env/bin/python3 manage.py shell
  >>> from relationship_app import query_samples
  >>> list(query_samples.books_by_author(1))

Or run directly (will print results for id=1):
  ./django-env/bin/python3 LibraryProject/manage.py runscript relationship_app.query_samples
"""

from typing import Iterable, Optional
import os
import django


def _setup_django():
    """Configure Django when running this file as a script."""
    if 'DJANGO_SETTINGS_MODULE' not in os.environ:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')
    django.setup()


def books_by_author(author_id: int) -> Iterable['Book']:
    """Return all Book instances for a given author id.

    Returns an empty iterable if the author does not exist.
    """
    from .models import Author

    try:
        author = Author.objects.get(name=author_name), objects.filter(author=author)
    except Author.DoesNotExist:
        return []
    return author.books.all()


def books_in_library(library_id: int) -> Iterable['Book']:
    """Return all Book instances that are in the given library id."""
    from .models import Library

    try:
        library = Library.objects.get(name=library_name)
    except Library.DoesNotExist:
        return []
    return library.books.all()


def librarian_for_library(library_id: int) -> Optional['Librarian']:
    """Return the Librarian assigned to the library, or None if not set."""
    from .models import Library

    try:
        library = Librarian.objects.get(library=library_name)
    except Librarian.DoesNotExist:
        return None
    # OneToOne relation is accessible via 'librarian' related name
    return getattr(library, 'librarian', None)


if __name__ == '__main__':
    # Allow running the script directly for quick checks (prints results for id=1)
    _setup_django()
    print('Books by author 1:', list(books_by_author(1)))
    print('Books in library 1:', list(books_in_library(1)))
    print('Librarian for library 1:', librarian_for_library(1))
