from rest_framework import viewsets, permissions
from rest_framework.response import Response
# Imports dos models e serializers
from ..models import Task, Equipment, Environment, TaskStatus, TaskStatusImage, CustomUser, Category
from ..serializers.task import TaskReadSerializer, TaskWriteSerializer
from ..serializers.equipment import EquipmentSerializer
from ..serializers.environment import EnvironmentSerializer
from ..serializers.task_status import TaskStatusSerializer, TaskStatusImageSerializer
from ..serializers.custom_user import CustomUserSerializer
from ..serializers.category import CategorySerializer

class TaskView(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,      # 1. Tem que estar logado
        permissions.DjangoModelPermissions # 2. Tem que ter a permissão exata no Admin
    ]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TaskReadSerializer
        return TaskWriteSerializer

    def get_queryset(self):
        """
        Este método define QUAIS dados serão retornados.
        """
        user = self.request.user
        
        # Se o usuário não estiver autenticado (por segurança extra), retorna lista vazia
        if not user.is_authenticated:
            return Task.objects.none()

        # Verifica se o usuário pertence ao grupo 'Técnico' (ou 'Tecnico')
        # Ajuste a string dentro de filter(name=...) para o nome EXATO do seu grupo no Admin
        is_technician = user.groups.filter(name__in=['Técnico', 'Tecnico', 'Técnico(a)']).exists()

        # REGRA:
        # 1. Se for Superusuário ou Técnico: Vê TUDO.
        # 2. Se for Colaborador comum: Vê APENAS o que ele criou (creator_FK=user).
        if user.is_superuser or is_technician:
            return Task.objects.all().order_by('-creation_date')
        else:
            return Task.objects.filter(creator_FK=user).order_by('-creation_date')

    # Para atribuir o criador automaticamente
    def perform_create(self, serializer):
    # Apenas salva a tarefa e define quem criou.
    # A responsabilidade de criar o primeiro status (com comentário e anexo)
    # agora é inteiramente do Frontend.
        serializer.save(creator_FK=self.request.user)