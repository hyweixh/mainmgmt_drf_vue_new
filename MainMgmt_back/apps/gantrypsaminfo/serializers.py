import time
from rest_framework import serializers
from django.db import transaction
from .models import Gantrypsaminfo
class GantryPsamInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gantrypsaminfo
        fields = '__all__'

    def create(self, validated_data):
        # 获取 psamno
        psamno = validated_data.get('psamno')

        # 使用事务管理来确保原子性
        with transaction.atomic():
            # 尝试获取已存在的 gantry_psam_info
            gantry_psam_info = Gantrypsaminfo.objects.filter(psamno=psamno).first()
            # print("gantry_psam_info", gantry_psam_info)
            if gantry_psam_info:
                # 如果存在，则更新它
                for key, value in validated_data.items():
                    setattr(gantry_psam_info, key, value)
                gantry_psam_info.save()
            else:
                # 如果不存在，则创建它
                gantry_psam_info = Gantrypsaminfo.objects.create(**validated_data)

        return gantry_psam_info


    def update(self, instance, validated_data):
        # 可以直接访问validated_data来更新实例
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # 或者直接设置你想要的字段值
        instance.tollid = ''
        instance.position = ''
        instance.pilenumber = ''
        instance.rsuid = ''
        instance.controlid = 0
        instance.channelid = 0
        instance.statusName = '坏卡'
        instance.last_createtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # 更新最后创建时间

        instance.save()
        return instance
