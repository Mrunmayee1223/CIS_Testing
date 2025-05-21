# api/serializers.py
from rest_framework import serializers
from .models import CustomUser, Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure password is accepted and hidden
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)  # ✅ avoid KeyError
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

