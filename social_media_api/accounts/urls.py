from django.urls import path, include
from .views import RegisterView, LoginView, MeView, PostViewSet, CommentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'posts/(?P<post_pk>[^/.]+)/comments', CommentViewSet, basename='comment')

urlpatterns =[
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', MeView.as_view(), name='profile'),
    path('', include(router.urls)),
]