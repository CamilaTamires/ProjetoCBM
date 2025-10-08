# DENTRO DO ARQUIVO: core/views.py
from rest_framework import viewsets
from ..models.task import Task
# Importe os DOIS serializers de Task
from ..serializers.task import TaskReadSerializer, TaskWriteSerializer

class TaskView(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    # serializer_class = TaskSerializer # Apague ou comente esta linha

    # Este método mágico escolhe o serializer correto com base na ação
    def get_serializer_class(self):
        # Se a ação for 'list' (ver a lista) ou 'retrieve' (ver um detalhe)
        if self.action in ['list', 'retrieve']:
            return TaskReadSerializer
        # Para qualquer outra ação ('create', 'update', 'partial_update')
        return TaskWriteSerializer

# ... suas outras views continuam iguais