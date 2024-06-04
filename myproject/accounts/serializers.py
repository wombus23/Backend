from rest_framework import serializers
from .models import Chat
from .models import CustomUser

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],
            password=validated_data['password']
        )
        return user

class MessageSerializer(serializers.Serializer):
    sender = serializers.CharField(max_length=10)
    text = serializers.CharField()

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'