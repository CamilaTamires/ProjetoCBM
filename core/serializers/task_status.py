# DENTRO DE core/serializers/task_status.py
from rest_framework import serializers
from ..models import TaskStatus, TaskStatusImage, CustomUser # Make sure CustomUser is imported
from .custom_user import CustomUserSerializer

class TaskStatusImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatusImage
        fields = ['id', 'image', 'task_status_FK']

class TaskStatusSerializer(serializers.ModelSerializer):
    # Campo para leitura dos dados do usuário
    user_detail = CustomUserSerializer(source='user_FK', read_only=True) 
    
    # Campo para leitura das imagens associadas ao status
    images = TaskStatusImageSerializer(many=True, read_only=True, source='TaskStatusImage_task_status_FK')

    # Campo para escrita do usuário
    # Esse campo aceita o ID do usuário ao criar/atualizar um TaskStatus
    user_FK = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), 
        allow_null=True, 
        required=False  # Permite que o campo seja opcional
    )

    class Meta:
        model = TaskStatus
        fields = [
            'id', 
            'status', 
            'status_date', 
            'comment', 
            'task_FK', 
            'user_FK',     
            'user_detail',  
            'images'
        ]
        # Apenas alguns campos são somente leitura
        read_only_fields = ['id', 'status_date', 'images', 'user_detail'] 