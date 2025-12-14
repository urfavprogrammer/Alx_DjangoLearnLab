from django.urls import path
from .views import RegisterView, LoginView, MeView

urlpatterns =[
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', MeView.as_view(), name='profile'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterView

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]