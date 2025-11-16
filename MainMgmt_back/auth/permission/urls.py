from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'permission'
router = DefaultRouter(trailing_slash=False)
router.register(r'permissions', SysPermissionViewSet, basename='permissions')
router.register(r'role-permissions', SysRolePermissionViewSet, basename='role-permission')

urlpatterns = [
    path('permissions/export', SysPermissionExportView.as_view(), name='export_permissions'),
]

urlpatterns += router.urls