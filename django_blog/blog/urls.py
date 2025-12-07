from django.urls import path
from .views import views
from blog.views import post_views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('posts/', post_views.PostListView.as_view(), name='posts'),
    path('posts/<int:pk>/', post_views.PostDetailView.as_view(), name='post-detail'),
    path('posts/new/', post_views.PostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/edit/', post_views.PostUpdateView.as_view(), name='post-edit'),
    path('posts/<int:pk>/delete/', post_views.PostDeleteView.as_view(), name='post-delete'),
]