from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'category',CategoryView)
router.register(r'custom-user',CustomUserView)
router.register(r'environment',EnvironmentView)
router.register(r'equipment',EquipmentView)
router.register(r'notification',NotificationView)
router.register(r'task-status', TaskStatusView, basename='taskstatus')
router.register(r'task-status-image', TaskStatusImageView, basename='taskstatusimage')
router.register(r'task',TaskView)

urlpatterns = router.urls