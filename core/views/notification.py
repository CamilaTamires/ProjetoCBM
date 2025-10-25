from rest_framework.viewsets import ModelViewSet
from ..models import *
from ..serializers import *
from rest_framework import permissions

class NotificationView(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.DjangoModelPermissions]