from django.urls import path, include
from . import views
from .views import list_books, LibraryDetailView

app_name = 'relationship_app'

urlpatterns = [
    path('books/', list_books, name='book-list'),
    path('libraries/<int:pk>/', LibraryDetailView.as_view(), name='library-detail'),
]
