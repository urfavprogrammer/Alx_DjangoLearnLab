from rest_framework import generics
from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer


class BookList(generics.ListAPIView):
	"""API view to list all books."""
	queryset = Book.objects.all()
	serializer_class = BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    """API viewset to retrieve, create, update, and delete books."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer