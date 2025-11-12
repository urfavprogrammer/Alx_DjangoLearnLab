from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from books.views import list_books, LibraryDetailView

app_name = 'relationship_app'

urlpatterns = [
    path('books/', list_books, name='book-list'),
    path('libraries/<int:pk>/', LibraryDetailView.as_view(), name='library-detail'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    # Role-based views
    path('role/admin/', views.admin_view, name='admin-view'),
    path('role/librarian/', views.librarian_view, name='librarian-view'),
    path('role/member/', views.member_view, name='member-view'),
]
