from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet
from ..models import *
from ..serializers import *
from rest_framework import permissions

class TaskStatusView(viewsets.ModelViewSet):
    queryset = TaskStatus.objects.all()
    serializer_class = TaskStatusSerializer
    permission_classes = [permissions.DjangoModelPermissions]

class TaskStatusImageView(viewsets.ModelViewSet):
    queryset = TaskStatusImage.objects.all()
    serializer_class = TaskStatusImageSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    
    # --- 2. Adicione esta linha para habilitar os parsers ---
    parser_classes = (MultiPartParser, FormParser)