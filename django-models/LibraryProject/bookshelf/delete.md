# Delete the book and confirm deletion

from bookshelf.models import Book
book = Book.objects.get(title="Nineteen Eighty-Four", author="George Orwell", publication_year=1949)
book.delete()
books = Book.objects.all()
print(list(books))

# Expected output:
# []  # Empty list, confirming the book was deleted
