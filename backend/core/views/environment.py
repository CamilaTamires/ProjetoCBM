from rest_framework.viewsets import ModelViewSet
from ..models import *
from ..serializers import *
from rest_framework import permissions

class EnvironmentView(ModelViewSet):
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer
    permission_classes = [permissions.DjangoModelPermissions]