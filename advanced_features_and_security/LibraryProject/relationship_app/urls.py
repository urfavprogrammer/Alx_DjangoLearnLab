from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'relationship_app'

urlpatterns = [
    path('books/', views.list_books, name='book-list'),
    path('libraries/<int:pk>/', views.LibraryBooksView.as_view(), name='library-detail'),

    # Book management (permission protected)
    path('books/add_book/', views.add_book, name='book-add'),
    path('books/<int:pk>/edit_book/', views.edit_book, name='book-edit'),
    path('books/<int:pk>/delete/', views.delete_book, name='book-delete'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    path('register/', views.register, name='register'),

    # Role-based views
    path('role/admin/', views.admin_view, name='admin-view'),
    path('role/librarian/', views.librarian_view, name='librarian-view'),
    path('role/member/', views.member_view, name='member-view'),
]
