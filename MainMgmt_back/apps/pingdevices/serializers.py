# apps/pingdevices/serializers.py

from rest_framework import serializers
from .models import Pingdevices
from apps.devicemgmt.models import DeviceInfo, DeviceType


# ==================== 设备类型序列化器 ====================
class DeviceTypeSerializer(serializers.ModelSerializer):
    """设备类型序列化器"""

    class Meta:
        model = DeviceType
        fields = ['id', 'devicetypename']


# ==================== 设备信息序列化器 ====================
class DeviceInfoSerializer(serializers.ModelSerializer):
    """设备信息序列化器（从devicemgmt获取）"""
    devicetype = DeviceTypeSerializer(read_only=True)

    class Meta:
        model = DeviceInfo
        fields = ['id', 'position', 'devicename', 'deviceip', 'devicetype']


# ==================== Ping结果列表序列化器 ====================
class PingResultSerializer(serializers.ModelSerializer):
    """用于历史查询的Ping结果序列化器"""
    devicetype_name = serializers.CharField(source='devicetype.devicetypename', read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Pingdevices
        fields = '__all__'

    def get_status_display(self, obj):
        """状态中文显示"""
        status_map = {
            'online': '✅ 在线',
            'offline': '❌ 离线',
            'error': '⚠️ 检查失败',
            'checking': '⏳ 检查中'
        }
        return status_map.get(obj.inspectresult, '未知')


# ==================== Ping主序列化器 ====================
class PingdevicesSerializer(serializers.ModelSerializer):
    """
    主序列化器（用于CRUD操作）
    与模型字段完全对应
    """

    class Meta:
        model = Pingdevices
        fields = '__all__'