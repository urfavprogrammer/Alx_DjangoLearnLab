from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('post/', views.PostListView.as_view(), name='post'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post-edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/comment/new/', views.CommentCreateView.as_view(), name='add-comment'),
    path('comments/<int:pk>/edit/', views.CommentUpdateView.as_view(), name='edit-comment'),
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='delete-comment'),
]