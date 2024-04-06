from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uuid', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['uuid']

class AuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()