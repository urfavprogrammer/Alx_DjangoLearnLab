from django.urls import path, include
from . import views

app_name = 'relationship_app'

urlpatterns = [
    path('books/', views.list_books, name='book-list'),
    path('libraries/<int:pk>/', views.LibraryBooksView.as_view(), name='library-detail'),
]
