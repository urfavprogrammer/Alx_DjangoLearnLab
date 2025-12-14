from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet

posts = DefaultRouter()
posts.register(r'posts', PostViewSet)
posts.register(r'posts/(?P<post_pk>\d+)/comments', CommentViewSet)

urlpatterns = [
    path('', include(posts.urls)),
]
