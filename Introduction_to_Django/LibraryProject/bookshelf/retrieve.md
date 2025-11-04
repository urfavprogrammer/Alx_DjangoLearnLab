# Retrieve and display all attributes of the book just created

from bookshelf.models import Book
book = Book.objects.get(title="1984", author="George Orwell", publication_year=1949)
print(f"Title: {book.title}\nAuthor: {book.author}\nPublication Year: {book.publication_year}")

# Expected output:
# Title: 1984
# Author: George Orwell
# Publication Year: 1949
