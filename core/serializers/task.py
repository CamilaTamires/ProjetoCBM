from rest_framework import serializers
from ..models import Task

# Importação dos serializers que a versão de LEITURA irá usar
from .custom_user import CustomUserSerializer
from .equipment import EquipmentSerializer
from .task_status import TaskStatusSerializer
from ..models.custom_user import CustomUser

# Serializer de Escrita 
class TaskWriteSerializer(serializers.ModelSerializer):

   # Define que responsáveis são uma lista de IDs
    responsibles_FK = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=CustomUser.objects.all(),
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'name', 
            'description', 
            'suggested_date', 
            'urgency_level', 
            'equipments_FK', 
            'responsibles_FK'
        ]

# Serializer de Leitura MODIFICADO
class TaskReadSerializer(serializers.ModelSerializer):
    creator_FK = CustomUserSerializer(read_only=True, allow_null=True)
    equipments_FK = EquipmentSerializer(many=True, read_only=True)
    responsibles_FK = CustomUserSerializer(many=True, read_only=True)
    status_history = TaskStatusSerializer(
        many=True, 
        read_only=True, 
        source='TaskStatus_task_FK' # Usa o related_name do ForeignKey
    ) 

    class Meta:
        model = Task
        fields = [
            'id', 
            'name', 
            'description', 
            'suggested_date', 
            'urgency_level', 
            'creation_date', 
            'creator_FK', 
            'equipments_FK', 
            'responsibles_FK',
            'status_history' 
        ]