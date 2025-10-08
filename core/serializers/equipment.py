from rest_framework import serializers
from ..models import Equipment

# Importamos os serializers dos quais este depende
from .category import CategorySerializer
from .environment import EnvironmentSerializer

class EquipmentSerializer(serializers.ModelSerializer):
    # Definimos os campos de relação para usar os serializers aninhados
    environment_FK = EnvironmentSerializer(read_only=True)
    category_FK = CategorySerializer(read_only=True)

    class Meta:
        model = Equipment
        # Listamos os campos explicitamente para incluir os campos aninhados
        fields = ['id', 'name', 'code', 'description', 'environment_FK', 'category_FK']