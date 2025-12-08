from rest_framework.viewsets import ModelViewSet
from ..models import *
from ..serializers import *
from rest_framework import permissions

class EquipmentView(ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.DjangoModelPermissions]