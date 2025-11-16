from .models import *
from rest_framework import serializers


class SysPermissionSerializer(serializers.ModelSerializer):
    """
    权限序列化器
    """
    class Meta:
        model = SysPermission
        fields = '__all__'

class SysRolePermissionSerializer(serializers.ModelSerializer):
    """
    角色权限关联序列化器
    """
    class Meta:
        model = SysRolePermission
        fields = '__all__'
