# 设备类型/子网类型，不涉及增删改，之需要查询，ListAPIView就OK
import re
import io
import json
import pandas as pd
from django.db import transaction
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import viewsets, status
from .models import DeviceInfo, SubnetType, DeviceType
from .serializers import (DeviceInfoSerializer, SubnetworkSerializer, DeviceTypeSerializer,
                          DeviceinfoUploadSerializer)
from utils.encrypt import encrypt_pwd, decode_pwd


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

@csrf_exempt  # 如果你没有处理 CSRF 令牌，可以使用这个装饰器来免除 CSRF 检查
@require_POST  # 确保视图只处理 POST 请求
def decrypt_password_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # 解析请求体中的 JSON 数据
        decrypt_pwd_query = data.get('decrypt_pwd')
        # print("encrypted_password--", decrypt_pwd_query)
        if decrypt_pwd_query:
            decoded_password = decode_pwd(decrypt_pwd_query)
            return JsonResponse({'decoded_password': decoded_password})
        else:
            return JsonResponse({'error': '未提供加密密码'}, status=400)
    else:
        return JsonResponse({'error': '请求中指定的方法不被允许'}, status=405)

def is_hex_string(s):
    pattern = r'^[0-9a-fA-F]+$'
    return bool(re.match(pattern, s))
class DeviceInfoViewSet(viewsets.ModelViewSet):

    # 如果使用viewsets.ModelViewSet使，它集成了 CreateModelMixin, RetrieveModelMixin,
    # UpdateModelMixin, DestroyModelMixin, ListModelMixin
    queryset = DeviceInfo.objects.all()
    serializer_class = DeviceInfoSerializer

    # 获取设备列表
    def get_queryset(self):
        subnetwork_id = self.request.query_params.get('subnetwork_id')
        devicetype_id = self.request.query_params.get('devicetype_id')
        position = self.request.query_params.get('position')
        deviceip = self.request.query_params.get('deviceip')

        queryset = self.queryset

        if subnetwork_id:
            queryset = queryset.filter(subnetwork_id=subnetwork_id)
            # print("过滤后的queryset (subnetwork_id):", queryset.query)
        if devicetype_id:
            queryset = queryset.filter(devicetype_id=devicetype_id)
            # print("过滤后的queryset (devicetype_id):", queryset.query)
        if position:
            queryset = queryset.filter(position__icontains=position)
            # print("过滤后的queryset (position):", queryset.query)
        if deviceip:
            queryset = queryset.filter(deviceip__icontains=deviceip)
            # print("过滤后的queryset (deviceip):", queryset.query)

        return queryset.all()
    # ------------------------------------------------------------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  # 实例化序列化器并传入请求数据
        serializer.is_valid(raise_exception=True)  # 验证数据，如果数据无效则抛出 ValidationError

        # 现在可以安全地访问 validated_data
        ip_address = serializer.validated_data.get('deviceip', None)
        password_1 = serializer.validated_data.get('pwd1', None)
        password_2 = serializer.validated_data.get('pwd2', None)
        password_3 = serializer.validated_data.get('pwd3', None)
        password_4 = serializer.validated_data.get('pwd4', None)
        # new_pass = encrypt_pwd(password_1)
        # 加密密码
        if password_1:
            new_pass = encrypt_pwd(password_1)
            serializer.validated_data['pwd1'] = new_pass  # 更新序列化器中的密码为加密后的密码
        if password_2:
            new_pass2 = encrypt_pwd(password_2)
            serializer.validated_data['pwd2'] = new_pass2  # 更新序列化器中的密码为加密后的密码
        if password_3:
            new_pass3 = encrypt_pwd(password_3)
            serializer.validated_data['pwd3'] = new_pass3  # 更新序列化器中的密码为加密后的密码
        if password_4:
            new_pass4 = encrypt_pwd(password_4)
            serializer.validated_data['pwd4'] = new_pass4  # 更新序列化器中的密码为加密后的密码

        # 检查IP是否已存在
        if DeviceInfo.objects.filter(deviceip=ip_address).exists():
            error_massage = ip_address + '-->该IP地址已存在!'
            # 如果IP已存在，则抛出自定义错误
            # raise ValidationError({'deviceip': ['该IP地址已存在。']})
            return Response({"detail": error_massage}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 保存数据
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    # 注意：如果您不需要其他方法的自定义行为，您可以使用 ModelViewSet 而不需要单独引入 mixin
    # ModelViewSet 已经包含了创建、检索、更新、删除和列表的所有 mixin

    def update(self, request, *args, **kwargs):
        """PUT /api/devicemgmt/<pk>/"""
        # print('>>> 进入 update (PUT)')
        return self._do_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/devicemgmt/<pk>/"""
        # print('>>> 进入 partial_update (PATCH)')
        kwargs['partial'] = True
        return self._do_update(request, *args, **kwargs)

    # 公共更新逻辑
    def _do_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # IP 重复校验
        ip_address = serializer.validated_data.get('deviceip')
        if ip_address and DeviceInfo.objects.exclude(id=instance.id).filter(deviceip=ip_address).exists():
            return Response({"detail": f"{ip_address} --> 该IP地址已存在!"},
                            status=status.HTTP_400_BAD_REQUEST)

        # 密码：只有和库中密文不同才重新加密
        for i in (1, 2, 3, 4):
            raw = serializer.validated_data.get(f'pwd{i}')
            current_cipher = getattr(instance, f'pwd{i}', '') or ''
            # print(f'pwd{i} 前端值={raw} | 库密文={current_cipher} | equal={raw == current_cipher}')
            if raw is None or raw == current_cipher:
                continue
            if raw == '':
                serializer.validated_data[f'pwd{i}'] = ''
            else:
                serializer.validated_data[f'pwd{i}'] = encrypt_pwd(raw)
                # print(f'>>> pwd{i} 重新加密完成')

        self.perform_update(serializer)
        # ↓↓↓ 新增：刷新实例，保证解密用的是最新密文 ↓↓↓
        instance.refresh_from_db()  # ← 重新从数据库拿最新密文
        print('>>> 刷新后实例 pwd1 =', instance.pwd1)  # 应该是最新密文
        ser = self.get_serializer(instance)
        print('>>> 序列化后 pwd1_clear =', ser.data['pwd1_clear'])  # 应该是明文
        return Response(self.get_serializer(instance).data)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# ----------------------------------------------------------
# 获取子网、设备类型名称
from rest_framework.permissions import AllowAny  # ✅ 完全公开
class DeviceAndSubnetTypesView(APIView):
    permission_classes = [AllowAny]  # 任何人可访问

    def get(self, request, *args, **kwargs):
        device_types = DeviceType.objects.all()
        subnet_types = SubnetType.objects.all()
        data = {
            'device_types': [device.devicetypename for device in device_types],
            'subnet_types': [subnet.subnettypename for subnet in subnet_types],
        }
        return Response(data)

# 批量上传
class DeviceinfoUploadView(APIView):
    # permission_classes = [AllowAny]  # 批量上传不验证权限
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
            ips = []  # 用于收集IP地址
            for index, row in deviceinfo_df.iterrows():
                # 检查并处理 NaN 值
                row = row.fillna('')  # 将所有 NaN 值替换为空字符串（或者其他默认值）

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
                    print(device_info_list)
                except KeyError as e:
                    return Response({"detail": f"缺少字段: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # 再次检查数据库中是否已存在这些IP，以防止并发问题
                existing_ips = DeviceInfo.objects.filter(deviceip__in=ips).values_list('deviceip', flat=True)
                if existing_ips:
                    return Response({"detail": f"IP地址已存在: {', '.join(existing_ips)}"},
                                    status=status.HTTP_400_BAD_REQUEST)

                with transaction.atomic():
                    DeviceInfo.objects.bulk_create(device_info_list)
                return Response({"detail": "设备信息成功上传！"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": f"数据库保存错误: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)

# 下载到exels表
# class DeviceinfoDownloadView(APIView):
#     def get(self, request):
#         pks_raw = request.query_params.get('pks')
#         if pks_raw is None or pks_raw == 'null':  # 浏览器把 JS 的 null 转成字符串 "null"
#             queryset = DeviceInfo.objects.all()
#         else:
#             try:
#                 pks = json.loads(pks_raw)
#                 if not pks:  # 空列表也走全部
#                     queryset = DeviceInfo.objects.all()
#                 else:
#                     queryset = DeviceInfo.objects.filter(pk__in=pks)
#             except Exception:
#                 return Response({"detail": "设备参数错误！"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             result = queryset.values(
#                 'deviceip',
#                 'devicename',
#                 'position',
#                 'devicemanufacture',
#                 'unittype',
#                 'deviceserialnumber',
#                 'user1',
#                 'pwd1',
#                 'user2',
#                 'pwd2',
#                 'user3',
#                 'pwd3',
#                 'user4',
#                 'pwd4',
#                 'mem',
#                 'devicetype__devicetypename',
#                 'subnetwork__subnettypename',
#             )
#
#             # 创建 DataFrame
#             DeviceInfo_df = pd.DataFrame(list(result))
#
#             # 解密密码（空字符串跳过）,否则解密函数会出错
#             # lambda x: 匿名函数，把每个元素依次传进来，变量名叫 x,
#             # 如果 x 是空字符串/None/空列表等“假值”，就直接返回空字符串，不再解密。
#             # decode_pwd(x), 当x有内容时，才调用后端解密函数，把密文还原成明文
#             DeviceInfo_df['pwd1'] = DeviceInfo_df['pwd1'].apply(lambda x: decode_pwd(x) if x else '')
#             DeviceInfo_df['pwd2'] = DeviceInfo_df['pwd2'].apply(lambda x: decode_pwd(x) if x else '')
#             DeviceInfo_df['pwd3'] = DeviceInfo_df['pwd3'].apply(lambda x: decode_pwd(x) if x else '')
#             DeviceInfo_df['pwd4'] = DeviceInfo_df['pwd4'].apply(lambda x: decode_pwd(x) if x else '')
#
#             # 重命名列
#             DeviceInfo_df = DeviceInfo_df.rename(columns={
#                 "deviceip": "设备IP",
#                 "devicename": '设备名称',
#                 "position": '安装位置',
#                 "devicemanufacture": '设备厂商',
#                 "unittype": '设备型号',
#                 "deviceserialnumber": '设备序列号',
#                 "user1": '账号1',
#                 "pwd1": '密码1',
#                 "user2": '账号2',
#                 "pwd2": '密码2',
#                 "user3": '账号3',
#                 "pwd3": '密码3',
#                 "user4": '账号4',
#                 "pwd4": '密码4',
#                 "mem": '备注',
#                 "devicetype__devicetypename": '设备类型名称',
#                 "subnetwork__subnettypename": '子网类型名称',
#             })
#
#             # 构造响应
#             response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#             response['Content-Disposition'] = 'attachment; filename="设备信息.xlsx"'
#
#             with pd.ExcelWriter(response, engine='openpyxl') as writer:
#                 DeviceInfo_df.to_excel(writer, sheet_name='设备信息', index=False)
#
#             return response
#
#         except Exception as e:
#             print("err info----",e)
#             return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
from django.http import HttpResponse  # 确保导入这个
# views.py
# views.py
import io
import json
import pandas as pd
from django.http import HttpResponse  # ✅ 用于返回文件
from rest_framework.views import APIView
from rest_framework.response import Response  # ✅ 用于返回错误信息
from rest_framework import status
from utils.encrypt import decode_pwd
from .models import DeviceInfo
from django.http import HttpResponse #（用于文件下载）
from rest_framework.response import Response #（用于错误JSON响应）
from rest_framework.permissions import AllowAny  # ✅ 添加导入
class DeviceinfoDownloadView(APIView):
    """
    设备信息导出视图
    GET /api/devicemgmt/devices/export/?pks=[1,2,3]  # 导出指定设备
    GET /api/devicemgmt/devices/export/              # 导出全部设备
    """

    # ❌ 删除这一行：renderer_classes = []
    permission_classes = [AllowAny]  # ✅ 明确允许任何人访问（临时）
    def get(self, request):
        print(f"【调试】请求头包含Authorization: {'Authorization' in request.headers}")
        if 'Authorization' in request.headers:
            print(f"【调试】Authorization: {request.headers['Authorization'][:20]}...")

        try:
            # 1. 解析请求参数
            pks_raw = request.query_params.get('pks')
            print(f"【调试】接收到pks参数: {pks_raw}")

            # 2. 确定查询范围
            if pks_raw in (None, 'null', ''):
                print("【调试】未提供pks，将导出全部设备")
                queryset = DeviceInfo.objects.all()
            else:
                try:
                    pks = json.loads(pks_raw)
                    print(f"【调试】解析pks成功: {pks}")
                    if not isinstance(pks, list):
                        print("【错误】pks不是列表类型")
                        return Response({"detail": "pks参数必须是JSON数组格式"}, status=status.HTTP_400_BAD_REQUEST)
                    queryset = DeviceInfo.objects.filter(pk__in=pks) if pks else DeviceInfo.objects.all()
                except json.JSONDecodeError as e:
                    print(f"【错误】pks解析失败: {e}")
                    return Response({"detail": f"pks参数解析失败: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # 3. 从数据库提取原始数据
            print("【调试】开始从数据库提取数据...")
            raw_data = list(queryset.values(
                'deviceip', 'devicename', 'position', 'devicemanufacture',
                'unittype', 'deviceserialnumber', 'user1', 'pwd1', 'user2', 'pwd2',
                'user3', 'pwd3', 'user4', 'pwd4', 'mem',
                'devicetype__devicetypename', 'subnetwork__subnettypename',
            ))

            print(f"【调试】成功提取 {len(raw_data)} 条记录")
            if not raw_data:
                print("【警告】未查询到任何数据")
                return Response({"detail": "没有可导出的设备数据"}, status=status.HTTP_400_BAD_REQUEST)

            # 4. 转换为DataFrame
            print("【调试】创建DataFrame...")
            df = pd.DataFrame(raw_data)
            print(f"【调试】DataFrame创建成功，形状: {df.shape}")

            # 5. 解密密码字段
            print("【调试】检查decode_pwd函数...")
            print(f"【调试】decode_pwd类型: {type(decode_pwd)}")
            print(f"【调试】decode_pwd是否可调用: {callable(decode_pwd)}")

            def safe_decode(pwd, column_name):
                """安全解密单个密码"""
                if pd.isna(pwd) or str(pwd).strip() == '':
                    return ''
                try:
                    if not callable(decode_pwd):
                        raise TypeError(f"decode_pwd 不是可调用的函数，当前类型: {type(decode_pwd)}")
                    decoded = decode_pwd(str(pwd))
                    print(f"  【调试】{column_name}: 原始值长度 {len(str(pwd))} -> 解密后长度 {len(decoded)}")
                    return decoded
                except Exception as e:
                    print(f"  【警告】{column_name}列解密失败，值: {pwd}, 错误: {e}")
                    return f"**解密失败: {str(e)}**"

            # 处理所有密码列
            for i in range(1, 5):
                pwd_col = f'pwd{i}'
                if pwd_col in df.columns:
                    print(f"【调试】正在处理 {pwd_col} 列...")
                    df[pwd_col] = df[pwd_col].apply(lambda x: safe_decode(x, pwd_col))
                    print(f"  ✅ {pwd_col} 处理完成")

            # 6. 重命名列
            print("【调试】准备重命名列...")
            column_mapping = {
                "deviceip": "设备IP",
                "devicename": "设备名称",
                "position": "安装位置",
                "devicemanufacture": "设备厂商",
                "unittype": "设备型号",
                "deviceserialnumber": "设备序列号",
                "user1": "账号1",
                "pwd1": "密码1",
                "user2": "账号2",
                "pwd2": "密码2",
                "user3": "账号3",
                "pwd3": "密码3",
                "user4": "账号4",
                "pwd4": "密码4",
                "mem": "备注",
                "devicetype__devicetypename": "设备类型名称",
                "subnetwork__subnettypename": "子网类型名称",
            }

            existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
            print(f"【调试】将重命名 {len(existing_columns)} 列")
            if existing_columns:
                df = df.rename(columns=existing_columns)

            print(f"【调试】最终DataFrame列: {list(df.columns)}")

            # 7. 生成Excel
            print("【调试】开始生成Excel...")
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='设备信息', index=False)

            print("【调试】Excel生成成功")
            output.seek(0)
            excel_data = output.read()

            print(f"【调试】Excel文件大小: {len(excel_data)} 字节")

            # 8. 返回文件响应
            response = HttpResponse(
                excel_data,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="设备信息.xlsx"'
            response['Content-Length'] = len(excel_data)

            print("【调试】响应构建完成，准备返回文件...")
            return response  # ✅ DRF会自动识别这是原始响应

        except Exception as e:
            # 错误时使用 DRF Response 返回JSON
            print("【完整错误栈】:")
            import traceback
            traceback.print_exc()
            return Response(
                {"detail": f"导出失败: {type(e).__name__}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )