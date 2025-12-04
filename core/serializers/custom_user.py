from rest_framework import serializers
from ..models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):

    groups = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'groups']
        many= True