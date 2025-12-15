from rest_framework import serializers
from .models import Notification
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)
    target_title = serializers.CharField(source='target.title', read_only=True, allow_null=True)

    class Meta:
        model = Notification
        fields = ['id', 'actor', 'verb', 'target_title', 'read', 'created_at']
