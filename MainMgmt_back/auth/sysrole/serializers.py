from .models import *
from rest_framework import serializers


class SysRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysRole
        fields = '__all__'


class SysUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUserRole
        fields = '__all__'
