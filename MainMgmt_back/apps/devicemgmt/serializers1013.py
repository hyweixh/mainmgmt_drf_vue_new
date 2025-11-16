from rest_framework import serializers
from .models import DeviceInfo, DeviceType, SubnetType
from django.core.validators import FileExtensionValidator

class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = '__all__'


class SubnetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubnetType
        fields = '__all__'


class DeviceInfoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # id自动增长，无需序列化
    # read_only：这个参数，只会在将ORM模型序列化成字典时会将这个字段序列化
    # write_only：这个参数，只会在将data进行校验的时候才会用到
    devicetype = DeviceTypeSerializer(read_only=True)
    devicetype_id = serializers.IntegerField(write_only=True)
    subnetwork = SubnetworkSerializer(read_only=True)
    subnetwork_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = DeviceInfo
        fields = '__all__'



class  DeviceinfoUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        validators=[FileExtensionValidator(['xlsx', 'xls'])],
        error_messages={'required': '请上传文件！'}
    )
