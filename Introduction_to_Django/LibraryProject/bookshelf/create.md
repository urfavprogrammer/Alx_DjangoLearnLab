# Create a Book instance in Django shell

from bookshelf.models import Book
book = Book.objects.create(title="1984", author="George Orwell", publication_year=1949)
print(book)

# Expected output:
# Book object (2)  # or similar, indicating successful creation
