from rest_framework import serializers
from ..models import Task, TaskStatus

# Importamos os serializers que a versão de LEITURA irá usar
from .custom_user import CustomUserSerializer
from .equipment import EquipmentSerializer

# NOVO: Serializer simples, apenas para CRIAR e ATUALIZAR tasks.
# Ele entende os IDs que o formulário envia.
class TaskWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        # Inclui todos os campos do model, que por padrão aceitam IDs para FKs.
        fields = [
            'name', 
            'description', 
            'suggested_date', 
            'urgency_level', 
            'creator_FK', 
            'equipments_FK', 
            'responsibles_FK'
        ]

# Serializer complexo para LEITURA (o que já tínhamos, agora renomeado)
class TaskReadSerializer(serializers.ModelSerializer):
    # Usando os serializers aninhados para mostrar os dados completos
    creator_FK = CustomUserSerializer(read_only=True, allow_null=True)
    equipments_FK = EquipmentSerializer(many=True, read_only=True)
    responsibles_FK = CustomUserSerializer(many=True, read_only=True)
    
    # Campo "calculado" para o status
    current_status = serializers.SerializerMethodField()

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
            'current_status'
        ]

    def get_current_status(self, obj: Task):
        latest_status = TaskStatus.objects.filter(task_FK=obj).order_by('-status_date').first()
        if latest_status:
            return latest_status.status
        return None