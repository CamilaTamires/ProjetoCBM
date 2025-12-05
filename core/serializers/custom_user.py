from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserSerializer(BaseUserSerializer):
    # Essa linha mágica converte IDs [1] em Nomes ["Técnico"]
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta(BaseUserSerializer.Meta):
        model = User
        # Adicione 'groups' à tupla de campos existentes do Djoser
        fields = ('id', 'name', 'email', 'nif', 'groups')