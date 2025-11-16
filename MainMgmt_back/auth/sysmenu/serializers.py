from .models import *
from rest_framework import serializers
class SysMenuSerializer(serializers.ModelSerializer):
    """
    菜单表序列化，包含子菜单
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        """
        :param obj:检查当前 obj 是否有 children 属性
        :return:返回序列化后的子菜单列表
        """
        if hasattr(obj, "children"):
            serializerMenuList: list[SysMenuSerializer2] = list()
            for sysMenu in obj.children:
                serializerMenuList.append(SysMenuSerializer2(sysMenu).data)
            return serializerMenuList

    class Meta:
        model = SysMenu
        fields = '__all__'


class SysMenuSerializer2(serializers.ModelSerializer):
    """
    菜单序列化，不包含children字段
    """
    class Meta:
        model = SysMenu
        fields = '__all__'

class SysRoleMenuSerializer(serializers.ModelSerializer):
    """
    角色菜单关联表序列化
    """
    class Meta:
        model = SysRoleMenu
        fields = '__all__'
