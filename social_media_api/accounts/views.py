from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_400_BAD_REQUEST
            )
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    

class UserViewSet(viewsets.ReadOnlyModelViewSets):
    queryset = User.Objects.all()
    serializer_class = UserSerializer
    permission_class = [IsAuthenticated]

    @action(detail = True, methods=['post'])
    def follow(self, request, pk=None):
        user_to_follow == request.user
        if user_to_follow == request.user:
            return Response({'error': 'Cannot Follow Yourself'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.following.add(user_to_follow)
        return Response({'message': f'Now following {user_to_follow.username}'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        user_to_unfollow = self.get_object()
        request.user.following.remove(user_to_unfollow)
        return Response({'message': f'Unfollowed {user_to_unfollow.username}'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def following(self, request):
        following_users = request.user.following.all()
        serializer = self.get_serializer(following_users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def followers(self, request):
        followers = request.user.followers.all()
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)
    
