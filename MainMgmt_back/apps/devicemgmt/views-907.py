# 设备类型/子网类型，不涉及增删改，之需耀查询，ListAPIView就OK
from rest_framework.generics import ListAPIView
from rest_framework import viewsets, status
# from django.db.models import Prefetch

from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from .models import DeviceInfo, SubnetType, DeviceType
from .serializers import (DeviceInfoSerializer, SubnetworkSerializer, DeviceTypeSerializer,
                          DeviceinfoUploadSerializer)
import pandas as pd
# 获取子网类型api
class SubnetTypeListView(ListAPIView):
    # queryset = SubnetType.objects.all()
    queryset = SubnetType.objects.all().order_by('id')
    serializer_class = SubnetworkSerializer
    pagination_class = None  # 禁用分页

# 获取设备类型
class DeviceTypeListView(ListAPIView):
    # queryset = DeviceType.objects.all()
    queryset = DeviceType.objects.all().order_by('id')
    serializer_class = DeviceTypeSerializer
    pagination_class = None  # 禁用分页

class DeviceInfoViewSet(viewsets.ModelViewSet):

    # 如果使用viewsets.ModelViewSet使，它集成了 CreateModelMixin, RetrieveModelMixin,
    # UpdateModelMixin, DestroyModelMixin, ListModelMixin
    queryset = DeviceInfo.objects.all()
    serializer_class = DeviceInfoSerializer

    # 获取设备列表
    # def get_queryset(self):
    #     print("查询参数:", self.request.query_params)
    #     subnetwork_id = self.request.query_params.get('subnetwork_id')
    #     devicetype_id = self.request.query_params.get('devicetype_id')
    #     position = self.request.query_params.get('position')
    #     deviceip = self.request.query_params.get('deviceip')
    #
    #     queryset = self.queryset
    #
    #     if subnetwork_id:
    #         queryset = queryset.filter(subnetwork_id=subnetwork_id)
    #         print("过滤后的queryset (subnetwork_id):", queryset.query)
    #     if devicetype_id:
    #         queryset = queryset.filter(devicetype_id=devicetype_id)
    #         print("过滤后的queryset (devicetype_id):", queryset.query)
    #     if position:
    #         queryset = queryset.filter(position__icontains=position)
    #         print("过滤后的queryset (position):", queryset.query)
    #     if deviceip:
    #         queryset = queryset.filter(deviceip__icontains=deviceip)
    #         print("过滤后的queryset (deviceip):", queryset.query)
    #
    #     return queryset.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  # 实例化序列化器并传入请求数据
        serializer.is_valid(raise_exception=True)  # 验证数据，如果数据无效则抛出 ValidationError

        # 现在可以安全地访问 validated_data
        ip_address = serializer.validated_data.get('deviceip', None)

        # print('deviceip---', ip_address)

        # 检查IP是否已存在
        if ip_address and DeviceInfo.objects.filter(deviceip=ip_address).exists():
            # 如果IP已存在，则抛出自定义错误
            raise ValidationError({'deviceip': ['该IP地址已存在。']})
        else:
            # 保存数据
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 注意：如果您不需要其他方法的自定义行为，您可以使用 ModelViewSet 而不需要单独引入 mixin
    # ModelViewSet 已经包含了创建、检索、更新、删除和列表的所有 mixin
    '''
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # 获取要更新的实例
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 获取请求中的IP地址
        ip_address = serializer.validated_data.get('deviceip', None)

        # 检查IP地址是否已存在（排除当前实例）
        if ip_address and DeviceInfo.objects.exclude(id=instance.id).filter(deviceip=ip_address).exists():
            error_message = {'deviceip': ['该IP地址已存在。']}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

            # 如果没有错误，继续更新
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # 如果 'prefetch_related' 已被应用，则更新实例的缓存
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
    '''
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # 获取要更新的实例
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 获取请求中的IP地址
        ip_address = serializer.validated_data.get('deviceip', None)

        # 检查IP地址是否已存在（排除当前实例）
        if ip_address and DeviceInfo.objects.exclude(id=instance.id).filter(deviceip=ip_address).exists():
            # 如果IP已存在，则构造错误响应
            error_message = {'deviceip': ['该IP地址已存在。']}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

            # if errors:
            #     # 将所有错误信息以字符串形式拼接起来
            #     detail = list(errors.values())[0][0]
            #     # detail = list(serializer.errors.values())[0][0]
            #     return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
            # # 如果没有错误，继续更新
        else:
            self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # 如果 'prefetch_related' 已被应用，则更新实例的缓存
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# ----------------------------------------------------------
# 获取子网、设备类型名称
from rest_framework.views import APIView
from rest_framework.response import Response

class DeviceAndSubnetTypesView(APIView):
    def get(self, request, *args, **kwargs):
        device_types = DeviceType.objects.all()
        subnet_types = SubnetType.objects.all()
        data = {
            'device_types': [device.devicetypename for device in device_types],
            'subnet_types': [subnet.subnettypename for subnet in subnet_types],
        }
        return Response(data)

# 从exelx批量上传设备信息
class DeviceinfoUploadView(APIView):
    def post(self, request):
        serializer = DeviceinfoUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get('file')

            deviceinfo_df = pd.read_excel(file)
            deviceinfos = [] # 保存读取的信息
            for index, row in deviceinfo_df.iterrows():
                # 获取子网
                try:
                    subnettypename = SubnetType.objects.filter(name=row['子网']).first()
                    if not subnettypename:
                        return Response({"detail": f"{row['子网']}不存在！"}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({"detail": "文件中子网列不存在！"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    deviceip = row['设备IP'],
                    devicename = row['设备名称'],
                    position = row['安装位置'],
                    devicemanufacture = row['设备厂商'],
                    unittype = row['设备型号'],
                    deviceserialnumber = row['设备序列号'],
                    user1 = row['账号1'],
                    pwd1 = row['密码1'],
                    user2 = row['账号2'],
                    pwd2 = row['密码2'],
                    user3 = row['账号3'],
                    pwd3 = row['密码3'],
                    user4 = row['账号4'],
                    pwd4 = row['密码4'],
                    mem = row['备注'],
                    devicetype_id = split("-", row['服务器'])[0],
                    subnetwork_id = split("-", row['子网'])[0],

                    deviceinfos = DeviceInfo(
                        deviceip=deviceip,
                        devicename=devicename,
                        position=position,
                        devicemanufacture=devicemanufacture,
                        unittype=unittype,
                        deviceserialnumber=deviceserialnumber,
                        user1=user1,
                        pwd1=pwd1,
                        user2=user2,
                        pwd2=pwd2,
                        user3=user3,
                        pwd3=pwd3,
                        user4=user4,
                        pwd4=pwd4,
                        mem=mem,
                        devicetype_id=devicetype_id,
                        subnetwork_id=subnetwork_id,
                    )
                   # deviceinfos.set_password(password) 密码加密放在此
                    deviceinfos.append(deviceinfos) # 添加道deviceinfos
                except Exception:
                    return Response({"detail": "请检查文件中邮箱、姓名、部门名称！"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                # 原子操作（事务），一旦某个记录保存失败，所有都失败
                with transaction.atomic():
                    # 统一把数据添加到数据库中
                    DeviceInfo.objects.bulk_create(deviceinfos)
            except Exception:
                return Response({"detail": "设备数据添加错误！"}, status=status.HTTP_400_BAD_REQUEST)


        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)