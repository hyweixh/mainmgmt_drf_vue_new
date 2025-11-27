import re
import io
import json
import logging
import pandas as pd
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny  # 用于公开接口

# ✅ 导入自定义权限类
from auth.rbac.permissions.rbac_permission import CustomPermissionMixin

from .models import DeviceInfo, SubnetType, DeviceType
from .serializers import (
    DeviceInfoSerializer,
    SubnetworkSerializer,
    DeviceTypeSerializer,
    DeviceinfoUploadSerializer
)
from utils.encrypt import encrypt_pwd, decode_pwd


# ==================== 公开接口（无需登录） ====================

class SubnetTypeListView(ListAPIView):
    """子网类型列表 - 公开查询接口"""
    queryset = SubnetType.objects.all().order_by('id')
    serializer_class = SubnetworkSerializer
    pagination_class = None
    permission_classes = [AllowAny]  # 任何人可访问


class DeviceTypeListView(ListAPIView):
    """设备类型列表 - 公开查询接口"""
    queryset = DeviceType.objects.all().order_by('id')
    serializer_class = DeviceTypeSerializer
    pagination_class = None
    permission_classes = [AllowAny]  # 任何人可访问


class DeviceAndSubnetTypesView(APIView):
    """设备类型+子网类型（下拉选项用）- 公开接口"""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        device_types = DeviceType.objects.all()
        subnet_types = SubnetType.objects.all()
        data = {
            'device_types': [device.devicetypename for device in device_types],
            'subnet_types': [subnet.subnettypename for subnet in subnet_types],
        }
        return Response(data)


# ==================== 认证接口（需要登录） ====================

class DeviceInfoViewSet(viewsets.ModelViewSet):
    """
    设备信息管理视图
    集成RBAC权限控制，支持增删改查
    """
    queryset = DeviceInfo.objects.all()
    serializer_class = DeviceInfoSerializer

    # ✅ 添加权限验证
    permission_classes = [CustomPermissionMixin]

    # ✅ 权限码映射配置（使用字典格式支持自定义错误消息）
    '''
    devices:view
    devices:add
    devices:edit
    devices:delete
    devices:device-types
    devices:subnet-types
    devices:upload
    devices:download
    '''
    permission_code_map = {
        'create': {'code': 'devices:add', 'message': '您没有添加设备的权限'},
        'update': {'code': 'devices:edit', 'message': '您没有编辑设备的权限'},
        'partial_update': {'code': 'devices:edit', 'message': '您没有编辑设备的权限'},
        'destroy': {'code': 'devices:delete', 'message': '您没有删除设备的权限'},
        'list': {'code': 'devices:view', 'message': '您没有查看设备列表的权限'},
        'retrieve': {'code': 'devices:view', 'message': '您没有查看设备详情的权限'},
    }

    def get_queryset(self):
        """根据查询参数过滤设备列表"""
        subnetwork_id = self.request.query_params.get('subnetwork_id')
        devicetype_id = self.request.query_params.get('devicetype_id')
        position = self.request.query_params.get('position')
        deviceip = self.request.query_params.get('deviceip')

        queryset = self.queryset

        if subnetwork_id:
            queryset = queryset.filter(subnetwork_id=subnetwork_id)
        if devicetype_id:
            queryset = queryset.filter(devicetype_id=devicetype_id)
        if position:
            queryset = queryset.filter(position__icontains=position)
        if deviceip:
            queryset = queryset.filter(deviceip__icontains=deviceip)

        return queryset.all()

    def create(self, request, *args, **kwargs):
        """创建设备 - 自动加密密码"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 密码加密处理
        for i in range(1, 5):
            password = serializer.validated_data.get(f'pwd{i}')
            if password:
                serializer.validated_data[f'pwd{i}'] = encrypt_pwd(password)

        # IP重复校验
        ip_address = serializer.validated_data.get('deviceip')
        if DeviceInfo.objects.filter(deviceip=ip_address).exists():
            return Response(
                {"detail": f"{ip_address} --> 该IP地址已存在!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def _do_update(self, request, *args, **kwargs):
        """公共更新逻辑 - 自动加密变更的密码"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # IP重复校验（排除自身）
        ip_address = serializer.validated_data.get('deviceip')
        if ip_address and DeviceInfo.objects.exclude(id=instance.id).filter(deviceip=ip_address).exists():
            return Response(
                {"detail": f"{ip_address} --> 该IP地址已存在!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 密码加密处理（仅对变更的密码）
        for i in range(1, 5):
            raw = serializer.validated_data.get(f'pwd{i}')
            current_cipher = getattr(instance, f'pwd{i}', '') or ''
            if raw is None or raw == current_cipher:
                continue
            serializer.validated_data[f'pwd{i}'] = encrypt_pwd(raw) if raw else ''

        self.perform_update(serializer)
        instance.refresh_from_db()  # 刷新以获取最新密文
        return Response(self.get_serializer(instance).data)

    def update(self, request, *args, **kwargs):
        """PUT /api/devicemgmt/<pk>/"""
        kwargs['partial'] = False
        return self._do_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/devicemgmt/<pk>/"""
        kwargs['partial'] = True
        return self._do_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """删除设备"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== 敏感操作接口（严格权限） ====================

class DeviceinfoUploadView(APIView):
    """
    设备批量上传
    需要专门的批量导入权限
    """
    # ✅ 添加权限验证
    permission_classes = [CustomPermissionMixin]
    # permission_classes = [AllowAny]

    # ✅ 为自定义POST方法配置权限
    permission_code_map = {
        'post': {'code': 'devices:upload', 'message': '您没有批量上传设备的权限'},
    }

    def post(self, request):
        serializer = DeviceinfoUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = request.FILES.get('file')
            if not file:
                return Response({"detail": "文件未上传！"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                deviceinfo_df = pd.read_excel(file, sheet_name='Sheet1')
            except Exception as e:
                return Response({"detail": f"文件读取错误: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            device_info_list = []
            ips = []
            for index, row in deviceinfo_df.iterrows():
                row = row.fillna('')
                ip = row['设备IP']
                if ip in ips:
                    return Response({"detail": f"EXCEL表中IP地址重复: {ip}"}, status=status.HTTP_400_BAD_REQUEST)
                ips.append(ip)

                try:
                    device_info = DeviceInfo(
                        deviceip=row['设备IP'],
                        devicename=row['设备名称'],
                        position=row['安装位置'],
                        devicemanufacture=row['设备厂商'],
                        unittype=row['设备型号'],
                        deviceserialnumber=row['设备序列号'],
                        user1=row['账号1'],
                        pwd1=encrypt_pwd(row['密码1']),
                        user2=row['账号2'],
                        pwd2=encrypt_pwd(row['密码2']),
                        user3=row['账号3'],
                        pwd3=encrypt_pwd(row['密码3']),
                        user4=row['账号4'],
                        pwd4=encrypt_pwd(row['密码4']),
                        mem=row['备注'],
                        devicetype_id=row['设备类型'].split("-")[0],
                        subnetwork_id=row['子网'].split("-")[0],
                    )
                    device_info_list.append(device_info)
                except KeyError as e:
                    return Response({"detail": f"缺少字段: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # 数据库IP重复检查
            existing_ips = DeviceInfo.objects.filter(deviceip__in=ips).values_list('deviceip', flat=True)
            if existing_ips:
                return Response(
                    {"detail": f"IP地址已存在: {', '.join(existing_ips)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                with transaction.atomic():
                    DeviceInfo.objects.bulk_create(device_info_list)
                return Response({"detail": "设备信息成功上传！"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": f"数据库保存错误: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)


class DeviceinfoDownloadView(APIView):
    """
    设备信息导出
    需要专门的导出权限
    """
    # ✅ 修改权限验证（原AllowAny改为CustomPermissionMixin）
    permission_classes = [CustomPermissionMixin]

    # ✅ 为自定义GET方法配置权限
    permission_code_map = {
        'get': {'code': 'devices:download', 'message': '您没有导出设备信息的权限'},
    }

    def get(self, request):
        try:
            # ✅ 打印Authorization头（调试用）
            auth_header = request.headers.get('Authorization', '无')
            logger.info(f"Authorization头: {auth_header}")  # ✅ 使用已定义的logger

            # 1. 解析请求参数
            pks_raw = request.query_params.get('pks')

            # 2. 确定查询范围
            if pks_raw in (None, 'null', ''):
                queryset = DeviceInfo.objects.all()
            else:
                try:
                    pks = json.loads(pks_raw)
                    if not isinstance(pks, list):
                        return Response({"detail": "pks参数必须是JSON数组格式"}, status=status.HTTP_400_BAD_REQUEST)
                    queryset = DeviceInfo.objects.filter(pk__in=pks) if pks else DeviceInfo.objects.all()
                except json.JSONDecodeError as e:
                    return Response({"detail": f"pks参数解析失败: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # 3. 提取数据
            raw_data = list(queryset.values(
                'deviceip', 'devicename', 'position', 'devicemanufacture',
                'unittype', 'deviceserialnumber', 'user1', 'pwd1', 'user2', 'pwd2',
                'user3', 'pwd3', 'user4', 'pwd4', 'mem',
                'devicetype__devicetypename', 'subnetwork__subnettypename',
            ))

            if not raw_data:
                return Response({"detail": "没有可导出的设备数据"}, status=status.HTTP_400_BAD_REQUEST)

            # 4. 转换为DataFrame
            df = pd.DataFrame(raw_data)

            # 5. 解密密码字段
            def safe_decode(pwd, column_name):
                if pd.isna(pwd) or str(pwd).strip() == '':
                    return ''
                try:
                    return decode_pwd(str(pwd))
                except Exception as e:
                    return f"**解密失败: {str(e)}**"

            for i in range(1, 5):
                pwd_col = f'pwd{i}'
                if pwd_col in df.columns:
                    df[pwd_col] = df[pwd_col].apply(lambda x: safe_decode(x, pwd_col))

            # 6. 重命名列
            column_mapping = {
                "deviceip": "设备IP", "devicename": "设备名称", "position": "安装位置",
                "devicemanufacture": "设备厂商", "unittype": "设备型号", "deviceserialnumber": "设备序列号",
                "user1": "账号1", "pwd1": "密码1", "user2": "账号2", "pwd2": "密码2",
                "user3": "账号3", "pwd3": "密码3", "user4": "账号4", "pwd4": "密码4",
                "mem": "备注", "devicetype__devicetypename": "设备类型名称",
                "subnetwork__subnettypename": "子网类型名称",
            }
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

            # 7. 生成Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='设备信息', index=False)

            # 8. 返回文件
            excel_data = output.getvalue()
            response = HttpResponse(
                excel_data,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="设备信息.xlsx"'
            response['Content-Length'] = len(excel_data)
            return response

        except Exception as e:
            return Response(
                {"detail": f"导出失败: {type(e).__name__}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== 工具函数（保持现状） ====================

@csrf_exempt
@require_POST
def decrypt_password_view(request):
    """
    密码解密工具函数
    ⚠️ 注意：建议转换为APIView类视图以支持统一权限控制
    """
    # 如果需要权限控制，建议改为类视图
    if request.method == 'POST':
        data = json.loads(request.body)
        decrypt_pwd_query = data.get('decrypt_pwd')
        if decrypt_pwd_query:
            decoded_password = decode_pwd(decrypt_pwd_query)
            return JsonResponse({'decoded_password': decoded_password})
        else:
            return JsonResponse({'error': '未提供加密密码'}, status=400)
    else:
        return JsonResponse({'error': '请求中指定的方法不被允许'}, status=405)


def is_hex_string(s):
    """检查是否为十六进制字符串"""
    pattern = r'^[0-9a-fA-F]+$'
    return bool(re.match(pattern, s))