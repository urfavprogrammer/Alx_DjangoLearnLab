# Django Shell CRUD Operations for Book Model

## Create
```python
from bookshelf.models import Book
book = Book.objects.create(title="1984", author="George Orwell", publication_year=1949)
print(book)
# Expected output:
# Book object (1)  # or similar, indicating successful creation
```

## Retrieve
```python
book = Book.objects.get(title="1984", author="George Orwell", publication_year=1949)
print(f"Title: {book.title}\nAuthor: {book.author}\nPublication Year: {book.publication_year}")
# Expected output:
# Title: 1984
# Author: George Orwell
# Publication Year: 1949
```

## Update
```python
book.title = "Nineteen Eighty-Four"
book.save()
print(f"Updated Title: {book.title}")
# Expected output:
# Updated Title: Nineteen Eighty-Four
```

## Delete
```python
book.delete()
books = Book.objects.all()
print(list(books))
# Expected output:
# []  # Empty list, confirming the book was deleted
```
