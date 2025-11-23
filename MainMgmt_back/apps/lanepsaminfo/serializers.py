from rest_framework import serializers
from django.db import transaction
from .models import LanePsamInfo, PsamStatus  # 假设 PsamStatus 模型在同一个应用下


class PsamStatusSerializer(serializers.ModelSerializer):
    """
    用于序列化 PsamStatus 模型的简单序列化器。
    如果 PsamStatus 模型有更多字段，可以根据需要添加。
    """

    class Meta:
        model = PsamStatus
        fields = ['id', 'psamstatus']


class LanePsamInfoSerializer(serializers.ModelSerializer):
    psamstatus = PsamStatusSerializer(read_only=True)
    psamstatus_id = serializers.IntegerField(write_only=True)
    # psamstatus = serializers.PrimaryKeyRelatedField(queryset=PsamStatus.objects.all())
    # print("序列化中的psamstatus----", psamstatus)
    class Meta:
        model = LanePsamInfo
        fields = '__all__'

    def create(self, validated_data):
        # 获取 psamno
        psamno = validated_data.get('psamno')

        # 使用事务管理来确保原子性
        with transaction.atomic():
            # 尝试获取已存在的 LanePsamInfo
            lane_psam_info = LanePsamInfo.objects.filter(psamno=psamno).first()

            if lane_psam_info:
                # 如果存在，则更新它
                for key, value in validated_data.items():
                    setattr(lane_psam_info, key, value)
                lane_psam_info.psamstatus = psamstatus
                lane_psam_info.save()
            else:
                # 如果不存在，则创建它
                lane_psam_info = LanePsamInfo.objects.create(psamstatus=psamstatus, **validated_data)

        return lane_psam_info
