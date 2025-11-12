from django.urls import path, include
from . import views
from .views import list_books, LibraryBooksView

app_name = 'relationship_app'

urlpatterns = [
    path('books/', list_books, name='book-list'),
    path('libraries/<int:pk>/', LibraryBooksView.as_view(), name='library-detail'),
]
