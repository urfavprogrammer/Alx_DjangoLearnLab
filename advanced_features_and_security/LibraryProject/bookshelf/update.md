# Update the title of the book and save changes

from bookshelf.models import Book
book = Book.objects.get(title="1984", author="George Orwell", publication_year=1949)
book.title = "Nineteen Eighty-Four"
book.save()
print(f"Updated Title: {book.title}")

# Expected output:
# Updated Title: Nineteen Eighty-Four
