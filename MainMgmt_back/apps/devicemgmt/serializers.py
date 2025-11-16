# apps/devicemgmt/serializers.py
from rest_framework import serializers
from .models import DeviceInfo, DeviceType, SubnetType
from django.core.validators import FileExtensionValidator
from utils.encrypt import decode_pwd  # 你的解密函数

# ---------- 基础 ----------
class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = '__all__'


class SubnetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubnetType
        fields = '__all__'


# ---------- 设备 ----------
class DeviceInfoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    devicetype = DeviceTypeSerializer(read_only=True)
    devicetype_id = serializers.IntegerField(write_only=True)
    subnetwork = SubnetworkSerializer(read_only=True)
    subnetwork_id = serializers.IntegerField(write_only=True)

    # 仅用于 GET 单条：返回明码
    pwd1_clear = serializers.SerializerMethodField()
    pwd2_clear = serializers.SerializerMethodField()
    pwd3_clear = serializers.SerializerMethodField()
    pwd4_clear = serializers.SerializerMethodField()

    class Meta:
        model = DeviceInfo
        fields = [
            'id', 'deviceip', 'devicename', 'position', 'devicemanufacture',
            'unittype', 'deviceserialnumber',
            'user1', 'pwd1', 'user2', 'pwd2', 'user3', 'pwd3', 'user4', 'pwd4',
            'pwd1_clear', 'pwd2_clear', 'pwd3_clear', 'pwd4_clear',
            'mem', 'create_time', 'devicetype', 'subnetwork',
            'devicetype_id', 'subnetwork_id'
        ]
        extra_kwargs = {
            'pwd1': {'write_only': True},
            'pwd2': {'write_only': True},
            'pwd3': {'write_only': True},
            'pwd4': {'write_only': True},
        }

    def get_pwd1_clear(self, obj):
        return decode_pwd(obj.pwd1) if obj.pwd1 else ''

    def get_pwd2_clear(self, obj):
        return decode_pwd(obj.pwd2) if obj.pwd2 else ''

    def get_pwd3_clear(self, obj):
        return decode_pwd(obj.pwd3) if obj.pwd3 else ''

    def get_pwd4_clear(self, obj):
        return decode_pwd(obj.pwd4) if obj.pwd4 else ''


# ---------- 批量上传 ----------
# serializers.py
class DeviceInfoSerializer(serializers.ModelSerializer):
    # ---------- 关联字段 ----------
    devicetype = DeviceTypeSerializer(read_only=True)
    subnetwork = SubnetworkSerializer(read_only=True)
    devicetype_id = serializers.IntegerField(write_only=True)
    subnetwork_id = serializers.IntegerField(write_only=True)

    # 1. 读：返回明码（仅 GET）
    pwd1_clear = serializers.SerializerMethodField()
    pwd2_clear = serializers.SerializerMethodField()
    pwd3_clear = serializers.SerializerMethodField()
    pwd4_clear = serializers.SerializerMethodField()

    # 2. 写：接收明文（仅 POST/PATCH/PUT）
    pwd1 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    pwd2 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    pwd3 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    pwd4 = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = DeviceInfo
        fields = [
            'id', 'deviceip', 'devicename', 'position', 'devicemanufacture',
            'unittype', 'deviceserialnumber',
            'user1', 'user2', 'user3', 'user4',
            'pwd1_clear', 'pwd2_clear', 'pwd3_clear', 'pwd4_clear',  # 读
            'pwd1', 'pwd2', 'pwd3', 'pwd4',                         # 写
            'mem', 'create_time', 'devicetype', 'subnetwork',
            'devicetype_id', 'subnetwork_id'
        ]

    # 读：返回明码
    def get_pwd1_clear(self, obj): return decode_pwd(obj.pwd1) if obj.pwd1 else ''
    def get_pwd2_clear(self, obj): return decode_pwd(obj.pwd2) if obj.pwd2 else ''
    def get_pwd3_clear(self, obj): return decode_pwd(obj.pwd3) if obj.pwd3 else ''
    def get_pwd4_clear(self, obj): return decode_pwd(obj.pwd4) if obj.pwd4 else ''

    # 写：把明文转给数据库字段（create/update 都会走）
    def validate(self, attrs):
        for i in (1, 2, 3, 4):
            val = attrs.pop(f'pwd{i}', None)
            if val is not None:      # 传了值（含空串）才处理
                attrs[f'pwd{i}'] = val   # 明文，后面视图会加密
        return attrs

class DeviceinfoUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        validators=[FileExtensionValidator(['xlsx', 'xls'])],
        error_messages={'required': '请上传文件！'}
    )