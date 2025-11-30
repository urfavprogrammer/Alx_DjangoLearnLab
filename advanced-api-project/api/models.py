from django.db import models

# Create your models here.

"""
Data models for the API.

Models:
- Author: Represents a book author. Contains the author's name and any
    metadata about the author can be added here in future (bio, birthdate, etc.).
- Book: Represents a published book. Stores the book title, the year it was
    published and a ForeignKey link to the `Author` who wrote it.

Relationship:
An `Author` can have many `Book` instances. This is represented using a
one-to-many relationship: `Book.author` is a `ForeignKey` to `Author`. The
`related_name='books'` on the FK allows accessing an author's books using
`some_author.books.all()` which is convenient when serializing nested lists.
"""


class Author(models.Model):
        """Model for an author.

        Fields:
        - name: The full name of the author (string, max length 100).
        """
        name = models.CharField(max_length=100)

        def __str__(self):
                return self.name
    

class Book(models.Model):
        """Model for a book.

        Fields:
        - title: The book title (string, max length 200).
        - publication_year: The year the book was published (integer).
        - author: ForeignKey to `Author` establishing a many-to-one relationship
            (many books -> one author). `on_delete=models.CASCADE` means deleting an
            author will delete their books.
        """
        title = models.CharField(max_length=200)
        publication_year = models.IntegerField()
        author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)

        def __str__(self):
                return self.title